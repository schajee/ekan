# Easy Knowledge Archive Network (EKAN)

A simplified and 'Easier' version of a Knowledge Archive Network, inspired from CKAN and DKAN. 

Built with Python, Django, Django-REST, Vue, Bootstrap, and Font Awesome. 

## Installation
1. Install Python 3.7+ and PIP
2. Clone repository (`git clone https://github.com/schajee/ekan.git`)
3. Create virtual environment (`virtualenv env` and `source env/bin/activate`)
4. Install dependencies (`pip install -r requirements.txt`)
5. Run server (`python manage.py runserver`)

## Information Architecture
The system consists of a few basic entities...
* A Resource is the basic unit of information or data. A resource can be a file or a url to a file that contains data. 
* A Dataset is a collection of resources. Datasets are categorized into topics, and belong to an organisation. 
* An Organisation is a government entity that owns the data that it publishes. Organisations have managers who are responsible for maintaining the datasets and resources. 
* A Topic is a classification mechanism to tag datasets into thematic areas. This allows users to find related datasets. A dataset can belong to multiple topics. 

In addition, a resource can be of Type and Format, while a dataset is released under License. Organisation's managers are Staff users who have access to Admin for editing and managing content.