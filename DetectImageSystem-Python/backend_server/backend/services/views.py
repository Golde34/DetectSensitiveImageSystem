from django.shortcuts import render
from django.contrib.auth import login
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from serializers import UserSerializer, RegisterSerializer
from rest_framework.views import APIView
from urllib.parse import urlparse
from models import *
import os
from AIModel import AIModel
from AIModel import downloadImage as download_image
import uuid
import json
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timezone
from django.utils.timezone import utc


def safe_delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


pipe = AIModel.Pipe()
FILE_IMG_ROOT = '../img/'


class PredictView(APIView):
    def post(self, request):
        print("calling predict request...")
        img_save_list = []
        try:
            key = request.headers['Authorization']
            domain = urlparse(str(request.headers['Domain']))
            child = Child.objects.get(key=key)
            parent = child.parent
            if len(request.data) == 0:
                return Response(status=status.HTTP_200_OK, data=[])
            img_path_list = []
            for img_object in request.data:
                url = img_object['url']
                img_path_list.append(url)

            for i in range(len(img_path_list)):
                img_path = img_path_list[i]
                tail = ".png"
                if "." in img_path:
                    tail = img_path[img_path.rindex(".") - 1:]
                if tail.lower() not in [".png", ".jpg"]:
                    tail = ".png"
                img_save_list.append(FILE_IMG_ROOT + str(uuid.uuid4()) + tail)
            print("Downloading...")
            mapping = download_image.download_img(img_path_list, img_save_list)
            print('Downloaded')
            result_mapping = {}
            input_model = []
            for url, path in mapping:
                result_mapping[path] = url
                input_model.append(path)

            detect_result = pipe.detect(input_model)

            nude = 0
            sexy = 0
            safe = 0

            result_response = []
            for path in detect_result:
                label = detect_result[path]
                url = result_mapping[path]
                if str(label) == 'nude':
                    nude += 1
                elif str(label) == 'sexy':
                    sexy += 1
                elif str(label) == 'safe':
                    safe += 1
                result_response.append({
                    "url": str(url),
                    "label": str(label)
                })
            request_data = Requests(child=child, parent=parent, domain=domain, nude=nude, sexy=sexy, safe=safe)
            request_data.save()
            if DomainStatistic.objects.filter(child=child, parent=parent, domain=domain).exists():
                domain_statistic = DomainStatistic.objects.get(child=child, parent=parent, domain=domain)
                print('--', nude, "--", sexy, ' --', safe, '----')
                domain_statistic.nude = domain_statistic.nude + nude
                domain_statistic.sexy = domain_statistic.sexy + sexy
                domain_statistic.safe = domain_statistic.safe + safe
                domain_statistic.requestNumber = domain_statistic.requestNumber + 1
            else:
                domain_statistic = DomainStatistic(requestNumber=1, child=child, parent=parent, domain=domain,
                                                   nude=nude, sexy=sexy, safe=safe)
            domain_statistic.save()

            if nude + sexy + safe != 0:
                nude_percentage = float(nude) / float(nude + sexy + safe)
            else:
                nude_percentage = 0
            if nude_percentage > 0.5:
                notification = Notification(child=child, parent=parent, sensitivePercentage=nude_percentage,
                                            requestUrl=str(request.headers['Domain']))
                notification.save()
            child_nodes = Child.objects.filter(key=key, parent=parent)
            option = json.loads(child_nodes[0].option)
            # print(option)
            # Child(key=key, parent=request.user, name=child, option = json.dumps({'blockingsites': blockingsites}))
            response = {
                "blockingsites": option['blockingsites'],
                "result_response": result_response
            }
            print(response)
            print(f"Request from {key} in domain {domain} nude {nude} sexy {sexy} safe {safe}")
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            print("------Error Logging------")
            print(e)
            print('---End error---')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        finally:
            for path in img_save_list:
                safe_delete_file(path)


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        print("1")
        serializer = self.get_serializer(data=request.data)
        print("2")
        # print(serializer.dat042d0c9a-4768-43eb-b0d5-d176ad6c4ca9a)
        serializer.is_valid(raise_exception=True)
        print("OK")
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


class GenerateManageAccount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            data = request.data
            child = data['childname']
            blocking_sites = data['blockingsites']
            print(type(data['blockingsites']))
            print(data['blockingsites'])
            key = uuid.uuid4()
            child = Child(key=key, parent=request.user, name=child,
                          option=json.dumps({'blockingsites': blocking_sites}))
            child.save()
            return Response(status=status.HTTP_200_OK, data={"key": key})
        except Exception as e:
            print("\nGenerate code error\n", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CheckManageAccount(APIView):
    def post(self, request):
        try:
            print(request.data)
            child = Child.objects.get(key=request.data['key'])
            return Response(status=status.HTTP_200_OK, data=child.option)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetManageAccount(APIView):
    def post(self, request):
        try:
            parent = request.user
            childs = Child.objects.filter(parent=parent)
            data = []
            for child in childs:
                data.append({
                    "name": child.name,
                    "key": child.key,
                    "option": child.option
                })
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as e:
            print("\nGet manage code error\n", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateChildAccount(APIView):
    def post(self, request):
        try:
            parent = request.user
            data = request.data
            key = data['key']
            blockingsites = ["page1.com", "DVdeptrai.net", "page2.me"]
            child = Child.objects.filter(key=key, parent=parent).update(name="Dong Viet khong lam nua dau",
                                                                        option=json.dumps(
                                                                            {'blockingsites': blockingsites}))
            print("child", child)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print("Update error", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DeleteManageAccount(APIView):
    def post(self, request):
        try:
            parent = request.user
            data = request.data
            print(data)
            key = data['key']
            Child.objects.get(parent=parent, key=key).delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print("\nDelete manage code error\n", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NotificationViews(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            current = datetime.utcnow().replace(tzinfo=utc)
            # print(type(current))
            notifications = Notification.objects.filter(parent=request.user).order_by('-time')
            result = []
            for i in notifications:
                distance = current - i.time
                total_second = float(distance.total_seconds())
                if total_second < 60:
                    ago = str(int(total_second)) + 's'
                elif total_second / 60 < 60:
                    ago = str(int(total_second / 60)) + 'm'
                elif total_second / 60 / 60 < 24:
                    ago = str(int(total_second / 60 / 60)) + 'h'
                else:
                    ago = str(int(total_second / 60 / 60 / 24))
                result.append({
                    "ID": i.pk,
                    "time": ago,
                    "child": i.child.name,
                    "sensitivePercentage": i.sensitivePercentage,
                    "requestUrl": i.requestUrl,
                    "readed": i.readed,
                    "domain": urlparse(str(i.requestUrl)).netloc
                })
            return Response(status=status.HTTP_200_OK, data=result)
        except Exception as e:
            print("\nGet notification error\n", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StatisticView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            parent = request.user
            result = []
            domain_statistics = DomainStatistic.objects.filter(parent=parent)
            for domainStatistic in domain_statistics:
                sum = domainStatistic.nude + domainStatistic.sexy + domainStatistic.safe
                if sum == 0:
                    continue
                else:
                    percen = float(domainStatistic.nude) / float(sum)
                result.append({
                    "requestNumber": domainStatistic.requestNumber,
                    "domain": domainStatistic.domain,
                    "nude": domainStatistic.nude,
                    "sexy": domainStatistic.sexy,
                    "safe": domainStatistic.safe,
                    "percentage": percen,
                    "blocked": domainStatistic.blocked
                })
            result = sorted(result, key=lambda d: d["percentage"], reverse=True)

            return Response(status=status.HTTP_200_OK, data=result)
        except Exception as e:
            print("\nGet domain statistic error\n", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

            # {
#     "key": "child key",
#     "blockingSites": ["vlxx.net"]
# }

