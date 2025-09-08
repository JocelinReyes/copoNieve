from flask import Flask, request, jsonify, render_template
import numpy as np

app = Flask(__name__)

def koch_segment(p0, p1):
    v = p1 - p0
    pA = p0 + v/3
    pB = p0 + v*2/3
    peak = pA + (v/3) * np.exp(1j * np.pi/3)
    return np.array([p0, pA, peak, pB, p1])

def koch_curve(order: int, scale: float = 10.0):
    points = np.array([0 + 0j, scale + 0j])
    poly = points.copy()
    for _ in range(order):
        new_poly = [poly[0]]
        for i in range(len(poly) - 1):
            seg = koch_segment(poly[i], poly[i+1])
            new_poly.extend(seg[1:])
        poly = np.array(new_poly, dtype=complex)
    return poly.real.tolist(), poly.imag.tolist()

def koch_snowflake(order: int, scale: float = 10.0):
    # Triángulo equilátero
    angles = np.array([0, 2*np.pi/3, 4*np.pi/3, 0])
    points = scale * np.exp(1j * angles)
    poly = points.copy()

    for _ in range(order):
        new_poly = [poly[0]]
        for i in range(len(poly) - 1):
            seg = koch_segment(poly[i], poly[i+1])
            new_poly.extend(seg[1:])
        poly = np.array(new_poly, dtype=complex)

    return poly.real.tolist(), poly.imag.tolist()

def koch_half(order: int, scale: float = 10.0, side: str = "left"):
    # Triángulo inicial
    angles = np.array([0, 2*np.pi/3, 4*np.pi/3])
    points = scale * np.exp(1j * angles)

    # Dependiendo del lado, elegimos solo 2 puntos del triángulo
    if side == "left":
        poly = points[:2]  # lado izquierdo del triángulo
    else:
        poly = points[1:]  # lado derecho del triángulo
        poly = np.append(poly, poly[0])  # cerrar el lado

    # Aplicar Koch solo a esos segmentos
    for _ in range(order):
        new_poly = [poly[0]]
        for i in range(len(poly)-1):
            seg = koch_segment(poly[i], poly[i+1])
            new_poly.extend(seg[1:])
        poly = np.array(new_poly, dtype=complex)

    return poly.real.tolist(), poly.imag.tolist()




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/koch", methods=["GET"])
def koch_api():
    order = int(request.args.get("order", 3))
    mode = request.args.get("mode", "curve")

    if mode == "curve":
        x, y = koch_curve(order)
    elif mode == "half":
        side = request.args.get("side", "left")  # puede ser left o right
        x, y = koch_half(order, side=side)

    else:
        return jsonify({"error": "mode debe ser 'curve' o 'half'"}), 400

    return jsonify({"x": x, "y": y})

if __name__ == "__main__":
    app.run(debug=True)
