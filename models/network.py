from database import db


class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    owner = db.Column(db.Integer, nullable=False) 
    devices = db.relationship("device", backred="network") 

    def __init__(self, owner):
	self.owner = owner
	pass

    def delete(self) -> None:
        """
        Deletes this device.

        :return: None
        """

        db.session.delete(self)
        self.commit()

    def commit(self) -> None:
        """
        Commits changes to the database.

        :return: None
        """

        db.session.commit()

    @staticmethod
    def create(user, power) -> 'Network':
        """
        Creates a new network for a specified user.

        :param user: The owner's id
        :return: New device
        """

	network = Network(user)

        db.session.add(network)
        db.session.commit()

        return network
