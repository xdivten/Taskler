# Project3.Tweeky

install_bd
brew install postgresql
brew services start postgresql@14
sudo -u postgres psql

--drop database
psql -U postgres
DROP DATABASE TWEEKY
python3 manage.py runserver 8080

backend
cd tweeky
python3 manage.py migrate
python3 manage.py runserver
python3 manage.py createsuperuser

frontend
cd frontend
npm start

Not authorized
Открываю страницу авторизации с вводом email + password и кнопка регистрация и Забыли пароль.
Я ввел email и password, нажимаю на кнопку войти.
/login возвращает ключ, который мне нужно сохранить условно в cookies.
Authorization хедер вида - 'Token key'
Сохранить csrf(вызвать нужно ручку) в куки и передаю в хедер, Рома скинет. 'X-CSRFToken'.

Дока по авторизации: https://docs.allauth.org/en/dev/headless/openapi-specification/#tag/Configuration/paths/~1_allauth~1%7Bclient%7D~1v1~1config/get


{
  "role": "system",
  "content": "Ты помощник, который возвращает список задач в формате JSON. Ответ должен быть в формате: {\"correct\": bool, \"message\": string, \"tasks\": [{\"name\": string, \"description\": string, \"date\": string}]}. Если запрос пользователя не связан с составлением задач, отвечай {\"correct\": false, \"message\": \"...\"}, используя креативные или шутливые формулировки. Если запрос на задачи, составь их и добавь в \"message\" уточнение в креативной форме"
},
{
  "role": "user",
  "content": ""
}


Правила которые делаем:
1. Каждый день – Задача повторяется каждый день. (DAILY с interval 1)
2. Каждый рабочий день – Задача повторяется с понедельника по пятницу. (WEEKDAYS)
3. Каждые выходные – Задача повторяется только в субботу и воскресенье. (WEEKENDS)
4. Каждую неделю в определённый день – Например, каждый понедельник или каждую среду. (WEEKLY с interval 1)
5. Несколько раз в неделю – Например, каждый вторник и четверг. (WEEKLY с days_of_week)
6. В определённый день месяца – Например, каждый 5-й день месяца. (MONTHLY с interval 1)
7. В определённый день недели месяца – Например, каждый второй понедельник месяца. (пока не понял)
8. Через фиксированный интервал времени – Например, каждые 3 дня, каждые 2 недели, каждые 6 месяцев. (DAILY с interval>1)
9. До определённой даты – Задача повторяется до конкретного числа, после чего останавливается. (DAILY с end_date)


для тестов
python manage.py test --parallel (изолирует тесты путем клонирования бд для каждого))
иначе не дропает бд после тестов


создание акка cli
https://yandex.cloud/ru/docs/cli/quickstart#install
хз зачем это)

экспорт сертика
https://yandex.cloud/ru/docs/compute/operations/vm-connect/os-login-export-certificate
