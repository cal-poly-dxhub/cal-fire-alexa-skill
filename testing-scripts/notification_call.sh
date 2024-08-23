#!/bin/sh

curl -i -X POST 'https://api.amazonalexa.com/v1/proactive/notifications/stages/development'\
     -H 'Content-Type: application/json'\
     -H 'Authorization: [YOUR AUTHENTICATION TOKEN]' \
     -d '{
    "topic": {
        "id": "ProductDeals"
    },
    "notification": {
        "id": "notificationId172397412924",
        "view": {
            "parameters": {
                "en": {
                    "title": "Notification title",
                    "message": "THERES A FIRE near you"
                },
                "en-US": {
                    "title": "Notification title",
                    "message": "WARNING there is a fire near you "
                },
                "und": {
                    "title": "Notification title",
                    "message": "there is a fire near you"
                }
            }
        }
    },
    "targeting": {
        "type": "USER",
        "values": [
            {"id":"amzn1.ask.account.AMARSMN7DOL5Y3YDH5CXXNMUMF26RLPY7MXEIDO6F626O4CX2LA2LIIZIDJHJ666JUARCOTIQZBBTCZ4ILPYDYCBLYYKUSGWH3X3XWDJUWHZIQHJKWR37SOHWKTHZ5OGLBQUYN6SG6GDW6NU262MPELE47AIM5CQBEEKREWIAIFM3O2BOXQDUT3E7NFTOYKEFI7OEGBC3KYBVFESW4NXMFFMCWRZUHAIAQJ5RKL5TM"}
        ]
    }
}'


