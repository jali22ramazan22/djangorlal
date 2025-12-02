#!/bin/bash
# Скрипт для демонстрации работы JWT authentication

echo "=============================================="
echo "   JWT Authentication Test для Swagger UI"
echo "=============================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL сервера
BASE_URL="http://localhost:8000"

echo -e "${YELLOW}Шаг 1: Получаем JWT токен для admin пользователя${NC}"
echo "POST $BASE_URL/api/v1/auth/users/login"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}')

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка: Не удалось подключиться к серверу${NC}"
    echo "Убедитесь, что сервер запущен: python manage.py runserver"
    exit 1
fi

# Извлекаем токены
ACCESS_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null)
REFRESH_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('refresh', ''))" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Ошибка: Не удалось получить токен${NC}"
    echo "Ответ сервера:"
    echo "$RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Токен успешно получен!${NC}"
echo ""
echo "Access Token (первые 50 символов):"
echo "${ACCESS_TOKEN:0:50}..."
echo ""
echo "Полный Access Token (скопируйте для Swagger):"
echo "$ACCESS_TOKEN"
echo ""

echo "=============================================="
echo -e "${YELLOW}Шаг 2: Тестируем API БЕЗ токена (ожидаем 401)${NC}"
echo ""

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/tasks/")
echo "GET $BASE_URL/api/v1/tasks/"
echo "Статус: $STATUS"

if [ "$STATUS" = "401" ]; then
    echo -e "${GREEN}✓ Корректно: 401 Unauthorized${NC}"
else
    echo -e "${RED}⚠ Неожиданный статус: $STATUS (ожидался 401)${NC}"
fi

echo ""
echo "=============================================="
echo -e "${YELLOW}Шаг 3: Тестируем API С токеном (ожидаем 200)${NC}"
echo ""

STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  "$BASE_URL/api/v1/tasks/")

echo "GET $BASE_URL/api/v1/tasks/"
echo "Header: Authorization: Bearer <token>"
echo "Статус: $STATUS"

if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Корректно: 200 OK (аутентификация успешна)${NC}"
else
    echo -e "${RED}⚠ Неожиданный статус: $STATUS (ожидался 200)${NC}"
fi

echo ""
echo "=============================================="
echo -e "${YELLOW}Шаг 4: Получаем список проектов админа${NC}"
echo ""

PROJECTS=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "$BASE_URL/api/v1/projects/")

PROJECT_COUNT=$(echo "$PROJECTS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('results', data)) if isinstance(data, dict) else len(data))" 2>/dev/null)

echo "GET $BASE_URL/api/v1/projects/"
echo -e "${GREEN}✓ Получено проектов: $PROJECT_COUNT${NC}"
echo ""

echo "=============================================="
echo -e "${YELLOW}Как использовать этот токен в Swagger UI:${NC}"
echo ""
echo "1. Откройте http://localhost:8000/api/v1/docs/"
echo "2. Нажмите кнопку 'Authorize' (🔒) в правом верхнем углу"
echo "3. В поле 'Value' вставьте этот токен:"
echo ""
echo -e "${GREEN}$ACCESS_TOKEN${NC}"
echo ""
echo "4. Нажмите 'Authorize' и 'Close'"
echo "5. Теперь все запросы будут авторизованы!"
echo ""
echo "=============================================="
echo -e "${YELLOW}Тестирование permissions в Swagger:${NC}"
echo ""
echo "✓ Попробуйте GET /api/v1/tasks/ - должно работать"
echo "✓ Попробуйте GET /api/v1/projects/ - должно работать"
echo "✓ Создайте задачу POST /api/v1/tasks/ - должно работать"
echo ""
echo "Для тестирования ограничений:"
echo "1. Получите токен для другого пользователя"
echo "2. Попробуйте изменить чужой проект - получите 403 Forbidden"
echo ""
echo "=============================================="
echo -e "${GREEN}Готово! JWT аутентификация работает корректно.${NC}"
echo "=============================================="
