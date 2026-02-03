# FlatAI Reverse API Client 🔐

A sophisticated Python client designed to reverse-engineer and automate image generation on FlatAI. Unlike standard API wrappers, this tool implements a full **security handshake protocol** to extract dynamic verification tokens (Nonces) before execution.

## 🧠 Core Engineering Concepts

This script bypasses standard bot protection by mimicking a legitimate user session flow:

1.  **Nonce Handshake:** Initiates a `GET` request to the homepage to scrape the dynamic `ai_generate_image_nonce` security token using Regex.
2.  **Session Persistence:** Maintains a persistent `requests.Session` to ensure cookies and headers remain consistent between the handshake and the generation payload.
3.  **Sticky Proxy Rotation:** Generates unique session IDs for each attempt to rotate IPs while maintaining session stability during the request lifecycle.
4.  **Header Mimicry:** Replicates exact browser headers (`Sec-Ch-Ua`, `Origin`, `X-Requested-With`) to blend in with organic traffic.

## 🛠 Dependencies

* Python 3.x
* `requests`

## 🚀 Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/flatai-reverse-api-client.git](https://github.com/yourusername/flatai-reverse-api-client.git)
    cd flatai-reverse-api-client
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Open `main.py` and update the Proxy settings at the top:
    ```python
    LP_HOST = "your-proxy-host"
    LP_PORT = "port"
    LP_USER_BASE = "username"
    LP_PASS = "password"
    ```

4.  **Run the client:**
    ```bash
    python main.py
    ```

## ⚙️ How It Works (The Flow)

```mermaid
sequenceDiagram
    participant Client
    participant HomePage
    participant AjaxEndpoint
    
    Client->>HomePage: GET / (Handshake)
    HomePage-->>Client: HTML + Nonce Token
    Client->>Client: Extract Nonce via Regex
    Client->>AjaxEndpoint: POST (Prompt + Nonce + Cookies)
    AjaxEndpoint-->>Client: JSON Response (Image URL)
    Client->>Client: Download Image
