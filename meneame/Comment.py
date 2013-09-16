class Comment(object):

    def get_id(self):
        return self.__id


    def get_number(self):
        return self.__number


    def get_user(self):
        return self.__user


    def get_comment(self):
        return self.__comment


    def get_votes(self):
        return self.__votes


    def get_date(self):
        return self.__date
    
    def get_url(self):
        return self.__url

    def set_id(self, value):
        self.__id = value


    def set_number(self, value):
        self.__number = value


    def set_user(self, value):
        self.__user = value


    def set_comment(self, value):
        self.__comment = value


    def set_votes(self, value):
        self.__votes = value


    def set_date(self, value):
        self.__date = value
        
    def set_url(self, value):
        self.__url = value

    def del_id(self):
        del self.__id


    def del_number(self):
        del self.__number


    def del_user(self):
        del self.__user


    def del_comment(self):
        del self.__comment


    def del_votes(self):
        del self.__votes


    def del_date(self):
        del self.__date
    
    def del_url(self):
        del self.__url
    
    id = property(get_id, set_id, del_id, "id's docstring")
    url = property(get_url, set_url, del_url, "url's docstring")
    number = property(get_number, set_number, del_number, "number's docstring")
    user = property(get_user, set_user, del_user, "user's docstring")
    comment = property(get_comment, set_comment, del_comment, "comment's docstring")
    votes = property(get_votes, set_votes, del_votes, "votes's docstring")
    date = property(get_date, set_date, del_date, "date's docstring")
    
    