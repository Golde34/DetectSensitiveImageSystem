import torch
import torch.nn as nn
import timm
import os
import os.path as path
from PIL import Image as ImgPIL

import torchvision.models
import torchvision.transforms as transforms


class EfficientNetV2(nn.Module):
    def __init__(self, pretrained=True, labels=1) -> None:
        super(EfficientNetV2, self).__init__()
        self.backbone = timm.create_model('tf_efficientnetv2_b3', pretrained=pretrained)
        self.backbone.classifier = nn.Linear(self.backbone.classifier.in_features, labels)

    def forward(self, x) -> torch.Tensor:
        out = self.backbone(x)
        return out


class Pipe:
    def __init__(self, model_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'EffNetV2_porn2.pt')):
        self.val_aug = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.label = ['nude', 'sexy', 'safe']
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.efficient_b0 = torchvision.models.mobilenet_v3_small(pretrained=True)
        self.efficient_b0.classifier[3] = nn.Linear(1024, 3)
        self.efficient_b0.load_state_dict(torch.load('moblienetv3_pretrained_0.9507401735579377.pt',
                                                     map_location=self.device))
        self.efficient_b0.eval()
        torch.no_grad()

    def detect(self, img_path_list):
        img_error = []
        img_success = []
        predict_result = {}
        img_list = []
        predicted_label = []
        for img_path in img_path_list:
            try:
                img = ImgPIL.open(img_path).convert("RGB")
                img = self.transform(img).unsqueeze(0)
            except Exception as e:
                img_error.append(img_path)
                continue

            predict_result[img_path] = ''
            img_success.append(img_path)
            img_list.append(img[0])

        if len(img_list) != 0:
            input = torch.stack(img_list, dim=0)
            input.to(self.device)
            outputs = self.efficient_b0(input)
            result = torch.max(outputs, 1)[1]
            predicted_label = [self.label[id] for id in result]
        index = 0
        assert len(predicted_label) == len(img_success)
        for img_path in img_success:
            predict_result[img_path] = predicted_label[index]
            index += 1
        for img_path in img_error:
            predict_result[img_path] = 'error'
        return predict_result

