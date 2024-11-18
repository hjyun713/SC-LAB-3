import torch.nn.functional as F
import torch.nn as nn

class Face_Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1,8,kernel_size=3, padding='same')
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3, padding='same')
        # self.conv3 = nn.Conv2d(16, 32, kernel_size=3, padding='same')
        # self.conv4 = nn.Conv2d(32, 64, kernel_size=3, padding='same')
        self.drop05 = nn.Dropout2d(p=0.5)
        self.drop25 = nn.Dropout1d(p=0.25)
        self.drop2d25 = nn.Dropout2d(p=0.25)
        self.fc1 = nn.Linear(44944,512)
        self.fc2 = nn.Linear(512,6)
        self.conv1_batchnorm = nn.BatchNorm2d(num_features=8)
        self.conv2_batchnorm = nn.BatchNorm2d(num_features=16)
        self.conv3_batchnorm = nn.BatchNorm2d(num_features=32)
        self.conv4_batchnorm = nn.BatchNorm2d(num_features=64)

    def forward(self,x):
        out = F.relu(self.conv1_batchnorm(self.conv1(x)))
        out = F.max_pool2d(out,3)
        out = F.relu(self.conv2_batchnorm(self.conv2(out)))
        # out = F.max_pool2d(out,2)
        # out = F.relu(self.conv3_batchnorm(self.conv3(out)))
        # out = F.max_pool2d(out,2)
        # out = F.relu(self.conv4_batchnorm(self.conv4(out)))
        out = F.max_pool2d(out,3)
        out = self.drop2d25(out)
        out = out.view(-1,44944)
        out = F.relu(self.fc1(out))
        out = self.drop25(out)
        out = self.fc2(out)
        out = F.softmax(out,dim=1)

        return out



# 희준에게.. 이스터에그
# # 파라미터 개수 확인
# numel_list = [p.numel() for p in model.parameters()]
# print(sum(numel_list), numel_list)