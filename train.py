import torch.nn.functional as F
import torch.nn as nn
import datetime
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os
import cv2
from model import Face_Net


class CustomDataset(Dataset):
    def __init__(self, data_folder, transform=None):
        self.data_folder = data_folder
        self.transform = transform
        self.image_paths = []  # 이미지 파일 경로를 저장할 리스트
        self.labels = []  # 클래스 레이블을 저장할 리스트

        # 데이터 폴더 내의 하위 폴더를 순회하면서 이미지 파일 경로와 클래스 레이블을 수집
        for class_label, class_folder in enumerate(sorted(os.listdir(data_folder))):  # 폴더 순회
            class_path = os.path.join(data_folder, class_folder)  # 클래스 폴더 경로
            if os.path.isdir(class_path):
                for image_name in os.listdir(class_path):  # 클래스 폴더 내의 이미지 파일 순회
                    image_path = os.path.join(class_path, image_name)
                    self.image_paths.append(image_path)
                    self.labels.append(class_label)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_name = self.image_paths[idx]
        image = cv2.imread(img_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = transforms.ToTensor()(image)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        label = F.one_hot(label,6)

        return image, label





def traing_loop(n_epochs, optimizer, model, loss_fn, train_loader):
    for epoch in range(1,n_epochs + 1):
        loss_train = 0.0

        for imgs, labels in train_loader:

            imgs = imgs.to(device='cuda').float()
            labels = labels.to(device='cuda').float()

            outputs = model(imgs)

            loss = loss_fn(outputs, labels)

            l2_lambda = 0.001
            l2_norm = sum(p.pow(2.0).sum() for p in model.parameters())
            loss += l2_lambda * l2_norm

            optimizer.zero_grad()

            loss.backward()

            optimizer.step()

            loss_train += loss.item()

        if epoch == 1 or epoch % 10 == 0:
            print(f'{datetime.datetime.now()} Epoch {epoch}, Training loss {loss_train/len(train_loader)}')


# 훈련 / 검증 비교 구문 ( 희준 필요하면 나중에 이걸로 정확도 테스트 가능 )
# def validate(model, train_loader, val_loader):
#     for name, loader in [("train", train_loader), ("val", val_loader)]:
#         correct = 0
#         total = 0
#
#         with torch.no_grad():
#             for imgs, labels in loader:
#                 imgs = imgs.to(device='cuda').float()
#                 labels = labels.to(device='cuda')
#
#                 outputs = model(imgs)
#                 _, predicted = torch.max(outputs, dim=1)
#                 total += labels.shape[0]
#                 correct += int((predicted == labels).sum())
#
#         print(f"Acc {name} : {correct / total:.2f}")
#
#
# validate(model, train_loader, test_loader)


if __name__=="__main__":
    data_folder = "BS_HBG_dataset/"


    batch_size = 16

    train_dataset = CustomDataset(data_folder=data_folder)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)


    model = Face_Net().to('cuda')
    optimizer = torch.optim.SGD(model.parameters(),lr=1e-2)
    loss_fn = nn.CrossEntropyLoss()


    traing_loop(
        n_epochs=10,
        optimizer=optimizer,
        model = model,
        loss_fn=loss_fn,
        train_loader=train_loader
    )

    torch.save(model.state_dict(),"face.pt")