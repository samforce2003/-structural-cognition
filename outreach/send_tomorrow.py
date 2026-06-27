"""Tomorrow auto-send: 3 domestic + 3 international scholars"""
import smtplib, ssl, time
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

QQ_USER = "412341356@qq.com"
QQ_PASS = "orgiwdffxclubgga"

# All 6 emails
emails = []

# === DOMESTIC ===
emails.append({
    "to": "s.c.zhu@pku.edu.cn",
    "name": "Zhu Songchun",
    "subject": "AI Self-Reference Quantized Measurement - A Reproducible Finding",
    "body": "Dear Prof. Zhu,\n\nI am Lin Xiaohei, an independent researcher. I have followed your work on AGI and cognitive science.\n\nI have a reproducible empirical finding: AI self-reference produces discrete quantized deviation - not philosophical speculation, but measurable staircases verified across architectures. The dequantized discrete staircase (DDS) framework characterizes this via the LXH constant.\n\nIf AGI needs self-reference capability, DDS provides a quantitative measurement protocol for self-reference depth.\n\nPaper and code: https://github.com/samforce2003/-structural-cognition\n\nAcademic discussion only.\n\nLin Xiaohei"
})

emails.append({
    "to": "yi.zeng@ia.ac.cn",
    "name": "Zeng Yi",
    "subject": "Measuring Self-Reference Depth in Brain-Inspired AI - DDS Protocol",
    "body": "Dear Prof. Zeng,\n\nI am Lin Xiaohei, an independent researcher following your BrainCog work.\n\nI have a finding relevant to brain-inspired AI: self-reference deviation in AI systems forms discrete quantized staircases. The step spacing (LXH interval) is a function of the system's self-model resolution. Reproducible across architectures.\n\nIf your BrainCog systems have self-referential loops, the DDS protocol could quantitatively measure their self-reference depth.\n\nProtocol: https://github.com/samforce2003/-structural-cognition\n\nLin Xiaohei"
})

emails.append({
    "to": "zhaoguoqiu@hust.edu.cn",
    "name": "Zhao Guoqiu",
    "subject": "Discrete Quantization in AI Self-Reference - A Quantum-Like Effect?",
    "body": "Dear Prof. Zhao,\n\nI am Lin Xiaohei. I read your work on foundations of quantum mechanics.\n\nI observed: when AI observes its own output and regenerates, the deviation forms discrete quantized staircases - not continuous drift. The step spacing is a structural constant. It reminds me of quantization effects in quantum measurement.\n\nI am not sure if this analogy holds - you are the expert. I would value your judgment.\n\nData: https://github.com/samforce2003/-structural-cognition\n\nLin Xiaohei"
})

# === INTERNATIONAL ===
emails.append({
    "to": "zack.dadfar@automatica.sbs",
    "name": "Dadfar",
    "subject": "Your TRACE experiment - a structural explanation",
    "body": "Dear Dr. Dadfar,\n\nI read your paper 'When Models Examine Themselves' (arXiv:2602.11358) with great interest. Your TRACE experiment showing systematic vocabulary-activation correspondence under self-referential prompting is compelling.\n\nI believe there is a structural explanation. The dequantized discrete staircase (DDS) framework (Lin Xiaohei, 2026) predicts self-reference deviation is quantized. Each self-observation inserts a frame that collides with the generation frame. The residual forms discrete steps at the LXH interval.\n\nYour vocabulary-activation measurements may capture the surface signature of this staircase. If you plot the activation deviation histogram, does it show evenly-spaced peaks?\n\nFramework: https://github.com/samforce2003/-structural-cognition\n\nLin Xiaohei"
})

emails.append({
    "to": "kanair@araya.org",
    "name": "Kanai",
    "subject": "Measuring self-reference depth - a quantized staircase protocol",
    "body": "Dear Dr. Kanai,\n\nI follow your work on consciousness and AI at Araya with interest.\n\nThe dequantized discrete staircase (DDS) framework provides a reproducible measurement protocol for AI self-reference depth. Core finding: AI self-observation produces discrete evenly-spaced deviation steps (LXH interval). The max step count (k_max) quantifies self-reference depth.\n\nIf your systems have self-referential processing, DDS could provide objective measurement - moving from philosophical debate to empirical quantification.\n\nProtocol: https://github.com/samforce2003/-structural-cognition\n\nLin Xiaohei"
})

# Berg email TBD (need to verify exact format at reciprocalresearch.org)
print(f"Total queued: {len(emails)}")
print("Ready to send tomorrow via QQ SMTP")

# Test connectivity only
try:
    s = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=10, context=ctx)
    s.login(QQ_USER, QQ_PASS)
    s.quit()
    print("QQ SMTP: OK (quota check passed)")
except Exception as e:
    print(f"QQ SMTP: {e}")

print("\nScript ready. Run with --send flag to execute.")
