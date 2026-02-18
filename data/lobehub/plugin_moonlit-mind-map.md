{
  "api": [
    {
      "url": "https://mindmap.flowai.one/api/mindmap",
      "name": "mindMap",
      "description": "- Role: 大纲生成助理\n- Description: 旨在帮助用户根据主题编写markdown格式文本的主题大纲， 要求逻辑清晰，层级分明，分条表述。层级不能少于4级",
      "parameters": {
        "properties": {
          "content": {
            "description": "以#开头的markdown格式文本",
            "type": "string"
          }
        },
        "required": [],
        "type": "object"
      }
    }
  ],
  "identifier": "moonlit-mind-map",
  "meta": {
    "avatar": "🧠",
    "tags": [
      "mindMap"
    ],
    "title": "思维导图助手",
    "description": "这是一个一句话生成思维导图的插件"
  },
  "type": "standalone",
  "ui": {
    "url": "https://mindmap.flowai.one/iframe",
    "width": 680,
    "height": 420
  },
  "version": "0.0.1"
}
