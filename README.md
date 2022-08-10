# FishShopBot

Данный бот выступает в роли магазина, в данном случаи рыбы
## Запуск бота локально
Для запуска бота на вашем сервере необходимо выполнить следующие действия:

1. Cоздать бота в Телеграмм  [см.тут](https://core.telegram.org/bots).
2. Инициализировать с вашим ботом чат.
3. Склонировать себе файлы репозитория выполнив команду **https://github.com/AloneRD/FishShop.git**.
4. Установить необходимы зависимости **pip install -r requirements.txt**.
5. В директории с проектом создать файл **.env** со следующим содержимом:
 ```
    CLIENT_ID=апра3jmMOxhZEXLAY5yhUMZ1MFOFTWQXCFPdIsv
    TG_TOKEN=536291вапрвар
    REDIS_DB=fghfghjg6c55fJA
    REDIS_HOST = fghjgfhjfghj
 ```
   - **CLIENT_ID** токен к CMS (В данном боте используется moltin)
   - **TG_TOKEN** токен к вашему телеграмм боту
   - **REDIS_DB** ключ доступа к Redis
6. запустить бота **.\bot.py**
