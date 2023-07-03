import requests

url = 'http://127.0.0.1:5000/remove_background'
image_path = 'colekt.jpg'
files = {'image': open(image_path, 'rb')}
response = requests.post(url, files=files)

if response.status_code == 200:
    with open('result.jpg', 'wb') as f:
        f.write(response.content)
    print('Arka plan kaldırma işlemi tamamlandı. Sonuç görüntüsü: result.jpg')
else:
    print('Arka plan kaldırma işlemi başarısız oldu.')

