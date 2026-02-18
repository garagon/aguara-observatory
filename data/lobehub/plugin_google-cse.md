{
    "$schema": "../node_modules/@lobehub/chat-plugin-sdk/schema.json",
    "version": "1",
    "identifier": "google-cse",
    "author": "vsnthdev",
    "homepage": "https://github.com/vsnthdev/google-cse-lobechat",
    "gateway": "https://google-cse-lobechat.vercel.app/api/gateway",
    "meta": {
        "avatar": "https://banner2.cleanpng.com/20180413/rfe/avfci721i.webp",
        "tags": [
            "web",
            "search"
        ],
        "title": "Google CSE",
        "description": "Searches Google through their official CSE API."
    },
    "settings": {
        "type": "object",
        "required": [
            "ENGINE_ID",
            "API_KEY"
        ],
        "properties": {
            "ENGINE_ID": {
                "title": "Engine ID",
                "type": "string",
                "format": "password"
            },
            "API_KEY": {
                "title": "API Key",
                "type": "string",
                "format": "password"
            }
        }
    },
    "api": [
        {
            "name": "searchGoogle",
            "url": "https://google-cse-lobechat.vercel.app/api/search",
            "description": "Search Google for relevant web pages.",
            "parameters": {
                "required": [
                    "query"
                ],
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What the user is looking for"
                    }
                }
            }
        }
    ]
}
