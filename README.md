Ustawianie zmiennej środowiskowej OPENAI_API_KEY (zalecane)
Aby program mógł korzystać z API OpenAI, należy ustawić zmienną środowiskową OPENAI_API_KEY z Twoim kluczem API.

Na systemie Linux / macOS
W terminalu wpisz:


export OPENAI_API_KEY="twój_klucz_openai"
Uwaga: ta komenda ustawi zmienną tylko na czas bieżącej sesji terminala.
Aby ustawić ją na stałe, dodaj powyższą linię do pliku ~/.bashrc, ~/.zshrc lub innego pliku konfiguracyjnego powłoki.

Na Windows
Wiersz poleceń (cmd):

set OPENAI_API_KEY=twój_klucz_openai
PowerShell:

$env:OPENAI_API_KEY="twój_klucz_openai"
Jeśli potrzebujesz pomocy z uzyskaniem klucza API, odwiedź platform.openai.com i utwórz nowy klucz w sekcji API Keys.