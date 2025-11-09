from fastapi.responses import HTMLResponse


def get_privacy_policy():
    return HTMLResponse(
        content="""
    <html>
    <head><title>Privacy Policy - iShout</title></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h1>Privacy Policy for iShout</h1>
        <p>At iShout, we respect your privacy. This Privacy Policy explains how we collect, use, and protect your information.</p>
        
        <h2>1. Information We Collect</h2>
        <p>We collect data such as your name, email, and Instagram profile information only when you connect your account through our platform.</p>

        <h2>2. How We Use Your Data</h2>
        <p>We use your data solely for providing app features such as posting, managing comments, and viewing analytics through the Instagram Graph API.</p>

        <h2>3. Data Sharing</h2>
        <p>We do not sell, trade, or share your data with third parties except Meta APIs required to provide our services.</p>

        <h2>4. Data Security</h2>
        <p>We implement encryption and secure storage to protect your data from unauthorized access.</p>

        <h2>5. Contact Us</h2>
        <p>If you have any questions, contact us at <a href="mailto:support@ishout.app">support@ishout.app</a>.</p>

        <p>Last Updated: November 2025</p>
    </body>
    </html>
"""
    )
