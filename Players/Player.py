#!/usr/bin/env python


class Player:

    """
    A base class representing an NFL player
    """

    def __init__(self, name, pos, college):
        """
        Initializes a Player object
        :param name:            - this player's name
        :param pos:             - this player's position
        :param college:         - where this player attended college
        """
        self.name = name
        self.pos = pos
        self.college = college

    def __repr__(self):
        return f'name: {str(self.name)}\n' \
               f'pos: {str(self.pos)}\n' \
               f'college: {str(self.college)}\n' \


    def __eq__(self, other):
        """
        Overloaded equality operator
        :param other:
        :return:
        """
        return self.name == other.name and \
            self.pos == other.pos and \
            self.college == other.college
