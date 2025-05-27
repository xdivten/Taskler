1. Установка клиента
устанавливаем cli
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

exec -l $SHELL или перезапускаем консоль

2. Логинимся
начинаем настройку профиля
yc init
с линка копируем токен, вставляем его и выбираем организацию, каталог, default Compute zone no

проверяем
yc config list

3. Экспорт ssh-сертификата
получаем список организаций
yc organization-manager organization list

получаем логин пользователя для органищзации
yc organization-manager os-login profile list \
  --organization-id <идентификатор_организации>

экспортируем сертификат
yc compute ssh certificate export \
    --login <логин_пользователя_или_сервисного_аккаунта> \
    --organization-id <идентификатор_организации> \
    --directory <путь_к_директории>
--directory можно не указывать, тогда будет храниться в ~/.ssh/

4. Коннектимся к серверу
первые два шага из 3 пункта

получаем список серверов
yc compute instance list

подключаемся к серверу
yc compute ssh \
  --name <имя_ВМ> или --id <идентификатор_ВМ>
  --login <логин_пользователя_или_сервисного_аккаунта>
--login можно не указывать, берется авторизованный юзер в yc cli




yc compute ssh --id fhmfvc6iduqdje74qi4v
