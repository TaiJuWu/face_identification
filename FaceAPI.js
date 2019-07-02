const params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
        'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
};
const faceAPI = {
    uri: "https://southeastasia.api.cognitive.microsoft.com/face/v1.0/detect",
    qs: params,
    method:"POST",
    body: chunkArray,
    headers: {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key' : subscriptionKey
    }
};
request(faceAPI, (error, response, data) => {
    var faceInfo = JSON.parse(data);
    if(event.source.type == 'user' || FourGroupId == '1a73' || FourGroupId == 'e893' || FourGroupId == 'f42e' || FourGroupId == 'e873'){
        
        replyMsg.push(faceInfo[0].faceAttributes.gender+', '+faceInfo[0].faceAttributes.age);
        console.log(replyMsg);
        sendMessage(event, replyMsg, UserMsg);
    }
});