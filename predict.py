from model import Face_Net
import torch
import cv2


def prediction(raw_img):
    try:
        model = Face_Net().to('cuda')
        model.load_state_dict(torch.load('face.pt'))
        model.eval()

        # 입력 데이터 형식 변경
        # print(raw_img.shape)
        # raw_img = cv2.cvtColor(raw_img,cv2.COLOR_BGR2GRAY)
        raw_img = torch.tensor(raw_img)
        raw_img = torch.unsqueeze(raw_img,0)
        raw_img = torch.unsqueeze(raw_img, 0)
        # raw_img = torch.permute(raw_img,(0,3,1,2))
        raw_img = raw_img.float().to('cuda')

        predicted = model(raw_img)
        print(predicted)
        # 최대값 뽑깅~
        y_label = torch.argmax(predicted,dim=1)
        HBG = y_label.item() + 1
        ACC = int(predicted[0][y_label].item() * 100)

        return HBG,ACC
    except Exception as e:
        print(f"infer error {e}")
