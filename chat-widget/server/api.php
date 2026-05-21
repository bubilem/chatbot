<?php
// server/api.php
require_once __DIR__ . '/config.php';

session_start();

header("Access-Control-Allow-Origin: " . CORS_ORIGIN);
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=UTF-8");

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Ensure the request method is POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["error" => "Method Not Allowed. Use POST."]);
    exit();
}

// Rate Limiting (max 1 request per second per session)
$minDelaySeconds = 1;
if (isset($_SESSION['last_request_time'])) {
    $timeSinceLastRequest = time() - $_SESSION['last_request_time'];
    if ($timeSinceLastRequest < $minDelaySeconds) {
        http_response_code(429);
        echo json_encode(["error" => "Příliš mnoho požadavků. Prosím zpomalte."]);
        exit();
    }
}
$_SESSION['last_request_time'] = time();

// Get the raw POST data
$rawData = file_get_contents("php://input");
$data = json_decode($rawData, true);

// Check if message is set
if (isset($data['message'])) {
    $userMessage = trim($data['message']);

    // Server-side validation
    if (empty($userMessage)) {
        http_response_code(400);
        echo json_encode(["error" => "Zpráva nemůže být prázdná."]);
        exit();
    }

    if (mb_strlen($userMessage) > 500) {
        http_response_code(400);
        echo json_encode(["error" => "Zpráva je příliš dlouhá (max 500 znaků)."]);
        exit();
    }

    // Forward the message to Python Bot API
    $postData = json_encode(['message' => $userMessage]);

    $ch = curl_init(BOT_API_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Content-Length: ' . strlen($postData)
    ]);
    curl_setopt($ch, CURLOPT_TIMEOUT, BOT_API_TIMEOUT);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    if ($response === false || $httpCode !== 200) {
        error_log("Bot API Curl Error: " . curl_error($ch));
        curl_close($ch);
        http_response_code(500);
        echo json_encode(["error" => "Omlouváme se, chatbot je momentálně nedostupný."]);
        exit();
    }
    curl_close($ch);

    // Bot API vrací přesně {"response": "Bot říká: ..."}
    $responseData = json_decode($response, true);
    if (isset($responseData['response'])) {
        echo json_encode(["response" => $responseData['response']]);
    } else {
        http_response_code(500);
        echo json_encode(["error" => "Neplatná odpověď od chatbota."]);
    }
} else {
    // Invalid request format
    http_response_code(400);
    echo json_encode(["error" => "Bad Request. 'message' field is required."]);
}
