import qrcode
import os

def generate_qr(cert_hash, host_url):
    verify_url = f"{host_url}verify?hash={cert_hash}"
    qr = qrcode.make(verify_url)
    filename = f"{cert_hash}.png"
    
    # Ensure folder exists
    os.makedirs(os.path.join("static", "qr"), exist_ok=True)
    path = os.path.join("static", "qr", filename)
    qr.save(path)
    
    return filename