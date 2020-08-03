# wekan-logstash

To format data for logstash and ELK (Kibana) - Format below :

    {"storyPoint": 2.0, "nbComments": 1, "createdBy": "fmonthel", "labels": ["vert", "jaune"], "members": ["fmonthel", "Olivier"], "id": "7WfoXMKnmbtaEwTnn", "createdAt": "2017-02-19T02:13:24.269Z", "lastModification": "2017-02-19T03:12:13.740Z", "list": "Todo", "dailyEvents": 5, "board": "Test", "isArchived": false, "duedAt": "2017-02-19T02:13:24.269Z", "swimlaneTitle": "Swinline Title", "customfieldName1": "value", "customfieldName2": "value", "assignees": "fmonthel"}
    {"storyPoint": 2.0, "nbComments": 1, "createdBy": "fmonthel", "labels": ["vert", "jaune"], "members": ["fmonthel", "Olivier"], "id": "7WfoXMKnmbtaEwTnn", "archivedAt": "2017-02-19T02:13:24.269Z", "createdAt": "2017-02-19T02:13:24.269Z", "lastModification": "2017-02-19T03:12:13.740Z", "list": "Done", "dailyEvents": 5, "board": "Test", "isArchived": true, , "duedAt": "2017-02-19T02:13:24.269Z", "swimlaneTitle": "Swinline Title", "customfieldName1": "value", "customfieldName2": "value", "assignees": "fmonthel"}

Goal is to export data into Json format that we can be used as input for Logstash and ElastisSearch / Kibana (ELK)

Import in logstash should be done daily basic (as we have field daily event)
