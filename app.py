from flask import Flask, request, jsonify
import cv2
import numpy as np
from matplotlib import pyplot as plt

app = Flask(__name__)

@app.route('/remove_background', methods=['POST'])
def remove_background():
    # Gelen görüntüyü alın
    file = request.files['image']
    image_bgr = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    if image_bgr is None:
        return jsonify({'error': 'Görüntü yüklenirken hata oluştu.'})

    # GrabCut ile nesnenin arka planını kaldırma
    mask = np.zeros(image_bgr.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # GrabCut için gerekli dikdörtgeni belirleme
    rectangle = (10, 10, image_bgr.shape[1] - 20, image_bgr.shape[0] - 20)

    cv2.grabCut(image_bgr, mask, rectangle, bgdModel, fgdModel, 10, cv2.GC_INIT_WITH_RECT)

    # GrabCut sonucunu iyileştirmek için maskeyi güncelleme
    mask_grabcut = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # Yumuşatma işlemi (blurring) ve kenar tespiti (Canny)
    blurred = cv2.blur(image_bgr, (5, 5))
    edges = cv2.Canny(blurred, 30, 100)

    # Kontur tespiti
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Kontur alanlarını kontrol ederek nesnenin dışını belirleme
    mask_contour = np.zeros(image_bgr.shape[:2], np.uint8)
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            cv2.drawContours(mask_contour, [contour], 0, (255), -1)

    # Maskeyi birleştirme
    mask_combined = cv2.bitwise_or(mask_grabcut, mask_contour)

    # Morfolojik işlemlerle maskenin kenarlarını yumuşatma
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Açma işlemi (opening) uygulayarak silinmeyen kısımları temizleme
    mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel, iterations=2)

    # Maskeyi kullanarak nesnenin dışını siyah yapma
    image_nobg = image_bgr.copy()
    image_nobg[np.where(mask_combined == 0)] = 0

    # Sonucu dönme
    _, img_encoded = cv2.imencode('.jpg', image_nobg)
    response = img_encoded.tobytes()

    return response

if __name__ == '__main__':
    app.run(debug=True)
