# 端點: https://westcentralus.api.cognitive.microsoft.com/face/v1.0
# 金鑰 1: fc50d5b8e8604b66a1f46d7526be4417
# 金鑰 2: 6be8c764a36d49a48dc26994dbe69bde

import requests
import json
import cv2
from matplotlib import pyplot as plt


subscription_key = 'fc50d5b8e8604b66a1f46d7526be4417'
assert subscription_key

face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/{0}'


data_headers = { 
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/octet-stream'
}


json_headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/json'
}
    

params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
}

# 輸入要是json
def write_json(data):
    with open('result.json' ,'w') as fp:
        json.dump(data,fp)

# 使用dectect的API
def detect_api(file_name):

    try:
        data = open('photo_src/{0}'.format(file_name) ,'rb')
        response = requests.post(face_api_url.format('detect'), params=params, headers=data_headers, data=data)
        return response.json()
    except Exception as err:
        print(err)


# 傳送多人的照片(test_data資料夾中的資料)
def test_data_classification(file_name):
    try:
        data = open('test_data/{0}'.format(file_name) ,'rb')
        response = requests.post(face_api_url.format('detect'), params=params, headers=data_headers, data=data)
        return response.json()
    except Exception as err:
        print(err)

# 創造person_group
def create_person_group(groupName):
    body = {
        "name": "group1",
        # "userData": "user-provided data attached to the person group.",
        "recognitionModel": "recognition_02"
        }
        # 要自己json.dumps不然會回傳為無效的參數
    resp = requests.put(face_api_url.format('persongroups') + '/' + groupName ,headers = json_headers ,data = json.dumps(body))
    try:
        # 失敗會回傳json格式
        print(resp.json())
        raise Exception('create group fail')
    except json.decoder.JSONDecodeError as err:
        # 成功回傳empty response
        print('create successfully ')
   
# 注意這邊的細節
# 取得face的retangle
def get_face_Rectangle(resp):
    faceRectangle = resp['faceRectangle']
    top = faceRectangle['top']
    left = faceRectangle['left']
    right = left + faceRectangle['height']
    bottom = top + faceRectangle['width']
    return ((left ,top) ,(right ,bottom))



# 傳送group給faceAPI
def get_group(faceIDs):
    group_resp = requests.post(face_api_url.format('group'),headers=json_headers,data=json.dumps(faceIDs))
    # print(json.dumps(group_resp.json()))
    # write_json(group_resp.json())
    return group_resp.json()

# 取得多人像片中的faceID與其對應的人臉辨識結果
def get_gruop_directory(group_response):
    group_directory = {}
    for i in range(len(group_response)):
        faceID = group_response[i]['faceId']
        rectangle = get_face_Rectangle(group_response[i])
        group_directory[faceID] = rectangle
    return group_directory


# 取得多人照片中的faceID
def get_group_faceId(group_response):
    group_ids = []
    for i in range(len(group_response)):
        face_ID = group_response[i]['faceId']
        group_ids.append(face_ID)
    return group_ids



# def draw_rectangle(rect,windows_name ,photo_src):
#     cv2.rectangle(photo_src , rect[0], rect[1] ,(0,255,0),3)
#     cv2.namedWindow(windows_name,cv2.WINDOW_NORMAL)
#     cv2.resizeWindow(windows_name,photo_src.shape[0],photo_src.shape[1])#定义frame的大小
#     cv2.imshow(windows_name,photo_src)
#     cv2.waitKey(0)
    # plt.imshow(photo_src,cmap='gray',interpolation = 'bicubic')



# 只是暫時這樣切，因為辨識的人物部分沒有跟main切開(第161列)
# # 要辨識的多人照片、faceID與name的鍵值對、要傳給faceAPI資料
def distinguish(photo_name ,face_and_name ,face_Ids):
    # 要辨識的多人照片
    multi_person_detection_response = test_data_classification(photo_name)

    # 取得多人圖片的faceUD與其對應的方框位置
    group_directory = get_gruop_directory(multi_person_detection_response)
    multi_person_faceID = get_group_faceId(multi_person_detection_response)
    face_Ids["faceIds"] = face_Ids["faceIds"] + multi_person_faceID
    
    # 使用group的API，回傳json的資料
    group_response = get_group(face_Ids)
    # write_json(group_directory)
    # print(group_directory)
    # print(json.dumps(group_response))

    # 創造兩位使用者的list
    skyHuan_group = list()
    imadog_group = list()
    print(group_response)


    # 提取不同人的group
    for group in group_response["groups"]:
        for ele in group:
            # 找出group裡面是否有skyHuan的ID
            if ele == skyHuan_id:
                skyHuan_group = group
                break
            if ele == imadog_id:
                imadog_group = group
                break

    img = cv2.imread('test_data/{0}'.format(photo_name))

    # 標示出skyHuan
    for face in skyHuan_group:
        if face != skyHuan_id:
            cv2.rectangle(img ,group_directory[face][0],group_directory[face][1] ,(0,255,0) ,3)
            cv2.putText(img, face_and_name[skyHuan_id], group_directory[face][0], cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 255), 1, cv2.LINE_AA)
    # 標示出imadog
    for face in imadog_group:
        if face != imadog_id:
            cv2.rectangle(img ,group_directory[face][0],group_directory[face][1] ,(0,255,0) ,3)
            cv2.putText(img, face_and_name[imadog_id], group_directory[face][0], cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 255), 1, cv2.LINE_AA)
    
    # 顯示圖案並存入資料夾中
    cv2.imwrite('face_api_result/result_{0}'.format(photo_name),img)
    # cv2.namedWindow(photo_name,cv2.WINDOW_NORMAL)
    # cv2.imshow(photo_name,img)
    # cv2.waitKey(0)
   


if __name__ == '__main__':
    # 劃出人臉正方形了
    skyHuan_response = detect_api('skyHuan.jpg')
    skyHuan_id = skyHuan_response[0]['faceId']
    # skyHuan_photo = cv2.imread('photo_src/skyHuan.jpg')
    # rect = get_face_Rectangle(skyHuan_response[0])
    # print(rect)
    # draw_rectangle(rect ,'imadog' ,skyHuan_photo)


    imadog_response = detect_api('imadog.jpg')
    imadog_id = imadog_response[0]['faceId']
    # imadog_photo = cv2.imread('photo_src/imadog.jpg')
    # rect = get_face_Rectangle(imadog_response[0])
    # # rect的格式為((left ,top) ,(right ,bottom))
    # draw_rectangle(rect ,'imadog' ,imadog_photo)
    

    ##get group and draw rectangle
    # group_photo_src = cv2.imread('test_data/test5.jpg')
    # group_response = test_data_classification('test5.jpg')
    # group_id = get_group_faceId(group_response)
    # for i in range(len(group_response)):
    #     rect = get_face_Rectangle(group_response[i])
    #     cv2.rectangle(group_photo_src , rect[0], rect[1] ,(0,255,0),3)
    # cv2.imshow('group' ,group_photo_src)
    # cv2.waitKey(0)



    # 儲存faceID:name 鍵值對
    face_and_name = {}
    face_and_name[skyHuan_id] = "skyHuan"
    face_and_name[imadog_id] = "imadog"

 
    # 傳送給faceAPI的body資料，輸入要辨識的faceID
    face_Ids = {
        "faceIds" : []
    }
    face_Ids["faceIds"].append(skyHuan_id)
    face_Ids["faceIds"].append(imadog_id)

    distinguish('test6.jpg',face_and_name,face_Ids)

    # # 有未知的錯誤
    # 錯誤應該loop中前一筆資料有關(沒清除完資料或是API的資料給錯了)
    # test_data = []
    # for i in range(1,7):
    #     test_data.append('test{0}.jpg'.format(i))
    
    # try:
    #     for data in test_data:
    #         distinguish(data,face_and_name,face_Ids)
    # except Exception:
    #     pass
    


    # # 暫時被放在distiguish中
    # # 要辨識的多人照片
    # photo_name = "test.jpg"
    # multi_person_detection_response = test_data_classification(photo_name)

    # # 取得多人圖片的faceUD與其對應的方框位置
    # group_directory = get_gruop_directory(multi_person_detection_response)
    # multi_person_faceID = get_group_faceId(multi_person_detection_response)
    # face_Ids["faceIds"] = face_Ids["faceIds"] + multi_person_faceID
    
    # # 使用group的API，回傳json的資料
    # group_response = get_group(face_Ids)
    # # write_json(group_directory)
    # # print(group_directory)
    # # print(json.dumps(group_response))

    # # 創造兩位使用者的list
    # skyHuan_group = list()
    # imadog_group = list()
    # print(group_response)


    # # 提取不同人的group
    # for group in group_response["groups"]:
    #     for ele in group:
    #         # 找出group裡面是否有skyHuan的ID
    #         if ele == skyHuan_id:
    #             skyHuan_group = group
    #             break
    #         if ele == imadog_id:
    #             imadog_group = group
    #             break

    # img = cv2.imread('test_data/{0}'.format(photo_name))

    # # 標示出skyHuan
    # for face in skyHuan_group:
    #     if face != skyHuan_id:
    #         cv2.rectangle(img ,group_directory[face][0],group_directory[face][1] ,(0,255,0) ,3)
    #         cv2.putText(img, face_and_name[skyHuan_id], group_directory[face][0], cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 255), 1, cv2.LINE_AA)
    # # 標示出imadog
    # for face in imadog_group:
    #     if face !=imadog_id:
    #         cv2.rectangle(img ,group_directory[face][0],group_directory[face][1] ,(0,255,0) ,3)
    #         cv2.putText(img, face_and_name[imadog_id], group_directory[face][0], cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 255), 1, cv2.LINE_AA)
    
    # # 顯示圖案並存入資料夾中
    # cv2.imwrite('face_api_result/result_{0}'.format(photo_name),img)
    # # cv2.namedWindow(photo_name,cv2.WINDOW_NORMAL)
    # # cv2.imshow(photo_name,img)
    # # cv2.waitKey(0)
   