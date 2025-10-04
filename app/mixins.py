from meta.views import MetadataMixin


class EKANMetaMixin(MetadataMixin):
    """Base mixin for EKAN meta tags"""
    
    meta_site_name = 'EKAN - Easy Knowledge Archive Network'
    meta_site_type = 'website'
    meta_keywords = ['open data', 'government data', 'datasets', 'transparency', 'public data']
    
    def get_meta_image(self, context=None):
        """Return default meta image"""
        return self.request.build_absolute_uri('/static/images/screenshot.png')
    
    def get_meta_url(self, context=None):
        """Return current page URL"""
        return self.request.build_absolute_uri()


class DatasetMetaMixin(EKANMetaMixin):
    """Meta mixin specifically for dataset pages"""
    
    def get_meta_title(self, context=None):
        if hasattr(self, 'object') and self.object:
            return f"{self.object.title} | EKAN"
        return "Datasets | EKAN"
    
    def get_meta_description(self, context=None):
        if hasattr(self, 'object') and self.object:
            return self.object.description or f"Dataset: {self.object.title}"
        return "Browse and download open government datasets"
    
    def get_meta_keywords(self, context=None):
        keywords = list(self.meta_keywords)
        if hasattr(self, 'object') and self.object:
            # Add dataset-specific keywords
            if hasattr(self.object, 'topics'):
                keywords.extend([topic.title for topic in self.object.topics.all()])
            if hasattr(self.object, 'organisation') and self.object.organisation:
                keywords.append(self.object.organisation.title)
        return keywords


class OrganisationMetaMixin(EKANMetaMixin):
    """Meta mixin specifically for organisation pages"""
    
    def get_meta_title(self, context=None):
        if hasattr(self, 'object') and self.object:
            return f"{self.object.title} | EKAN"
        return "Organizations | EKAN"
    
    def get_meta_description(self, context=None):
        if hasattr(self, 'object') and self.object:
            return self.object.description or f"Datasets published by {self.object.title}"
        return "Browse government organizations and their published datasets"
    
    def get_meta_keywords(self, context=None):
        keywords = list(self.meta_keywords)
        if hasattr(self, 'object') and self.object:
            keywords.extend([self.object.title, 'government organization'])
        return keywords


class ResourceMetaMixin(EKANMetaMixin):
    """Meta mixin specifically for resource pages"""
    
    def get_meta_title(self, context=None):
        if hasattr(self, 'object') and self.object:
            return f"{self.object.title} | {self.object.dataset.title} | EKAN"
        return "Resource | EKAN"
    
    def get_meta_description(self, context=None):
        if hasattr(self, 'object') and self.object:
            desc = self.object.description or f"Resource: {self.object.title}"
            return f"{desc} (Format: {self.object.format.title})"
        return "Download data resource"
    
    def get_meta_keywords(self, context=None):
        keywords = list(self.meta_keywords)
        if hasattr(self, 'object') and self.object:
            keywords.extend([
                self.object.format.title.lower(),
                self.object.dataset.title,
                'download'
            ])
        return keywords


class TopicMetaMixin(EKANMetaMixin):
    """Meta mixin specifically for topic pages"""
    
    def get_meta_title(self, context=None):
        if hasattr(self, 'object') and self.object:
            return f"{self.object.title} | Topics | EKAN"
        return "Topics | EKAN"
    
    def get_meta_description(self, context=None):
        if hasattr(self, 'object') and self.object:
            return self.object.description or f"Datasets related to {self.object.title}"
        return "Browse datasets by topic category"
    
    def get_meta_keywords(self, context=None):
        keywords = list(self.meta_keywords)
        if hasattr(self, 'object') and self.object:
            keywords.extend([self.object.title, 'topic', 'category'])
        return keywords