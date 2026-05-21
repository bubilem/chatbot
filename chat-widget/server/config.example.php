<?php
// =============================================
// Chat Widget – konfigurační šablona
// Zkopírujte tento soubor na "config.php" a upravte hodnoty.
// SOUBOR config.php NESMÍ BÝT NIKDY COMMITOVÁN DO GITU!
// =============================================

// URL běžícího Python (FastAPI) backendu
// Vývojové prostředí: http://127.0.0.1:8000/chat
// Produkce: nastavte na interní URL vašeho serveru
define('BOT_API_URL', 'http://127.0.0.1:8000/chat');

// Timeout pro volání Python API v sekundách
// LLM může generovat odpověď 15–60 s – hodnotu přizpůsobte výkonu serveru
define('BOT_API_TIMEOUT', 60);

// CORS – povolené domény pro přístup k této proxy
// Vývojové prostředí: '*'
// Produkce: nastavte konkrétní doménu, např. 'https://vase-domena.cz'
define('CORS_ORIGIN', '*');
