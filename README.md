# Easy Knowledge Archive Network (EKAN)
A simplified and 'Easier' version of a Knowledge Archive Network, inspired from CKAN and DKAN. Built with Python, Django, Django-REST, Vue, Bootstrap, and Font Awesome. 

![alt text](https://github.com/schajee/ekan/blob/master/web/static/images/screenshot.png "Logo Title Text 1")

## Information Architecture
The system consists of a few basic entities...
* A Resource is the basic unit of information or data. A resource can be a file or a url to a file that contains data. 
* A Dataset is a collection of resources. Datasets are categorized into topics, and belong to an organisation. 
* An Organisation is a government entity that owns the data that it publishes. Organisations have managers who are responsible for maintaining the datasets and resources. 
* A Topic is a classification mechanism to tag datasets into thematic areas. This allows users to find related datasets. A dataset can belong to multiple topics. 

In addition, a resource can be of a Format, while a dataset is released under a License. Organisation's managers are Staff users who have access to Admin for editing and managing content.
