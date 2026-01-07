(function () {
    const container = document.getElementById('wondrlink-chat-widget');
    if (!container) return;

    const apiUrl = container.getAttribute('data-api-url') || 'http://localhost:5001/api';

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = apiUrl.replace('/api', '') + '/index.html?mode=widget';
    iframe.style.width = '400px';
    iframe.style.height = '600px';
    iframe.style.border = 'none';
    iframe.style.position = 'fixed';
    iframe.style.bottom = '20px';
    iframe.style.right = '20px';
    iframe.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
    iframe.style.borderRadius = '12px';
    iframe.style.zIndex = '9999';

    document.body.appendChild(iframe);
})();
