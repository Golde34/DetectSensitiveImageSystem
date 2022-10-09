import os
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import urlparse
from backend_server.backend.services.models import *
import os
from backend_server.backend.services.AIModel import downloadImage as download_image, AIModel
import uuid
import json


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
