import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def detect_bars_and_extract_text(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro: A imagem em '{image_path}' não foi carregada.")
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detectar bordas
    edges = cv2.Canny(gray, 30, 100)  # Ajuste os limites conforme necessário

    # Dilatar bordas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dilated = cv2.dilate(edges, kernel, iterations=3)

    # Mostrar etapas de depuração
    cv2.imshow("Cinza", gray)
    cv2.imshow("Bordas", edges)
    cv2.imshow("Dilatação", dilated)
    cv2.waitKey(0)

    # Encontrar contornos
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bar_areas = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        print(f"Contorno: x={x}, y={y}, w={w}, h={h}")  # Depuração

        # Filtro de tamanho
        if h > 40 and w < 50:  # Ajuste os valores conforme necessário
            bar_areas.append((x, y, w, h))
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    print(f"Quantidade de barras detectadas: {len(bar_areas)}")

    # Extrair texto abaixo das barras
    extracted_text = []
    for (x, y, w, h) in bar_areas:
        roi = gray[y + h:y + h + 40, x:x + w]  # Região abaixo da barra
        cv2.imshow("ROI", roi)
        cv2.waitKey(0)
        text = pytesseract.image_to_string(roi, config='--psm 7')
        print(f"Texto extraído: {text.strip()}")
        extracted_text.append(text.strip())

    # Mostrar imagem final com contornos
    cv2.imshow("Barras Detectadas", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return extracted_text


# Testar a função
image_path = "/home/stuart/Documentos/OCR/capturas_sample200_VC/3.png"  # Caminho para a imagem
texts = detect_bars_and_extract_text(image_path)
print("Textos extraídos:", texts)
