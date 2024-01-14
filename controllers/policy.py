# blablaaaaaaaaaa

from typing import Dict, List
from datetime import datetime
from app import db
from models import Policy, Firewall
from exceptions import DatabaseError, IntegrityError, NotFoundInDB, GenericError


class PolicyContext:
    def __init__(self):
        # init session
        self.session = db.session

    def get_policy(self, pol_uuid: int) -> Dict:
        if pol_uuid:
            try:
                # get policy with id
                policy = Policy.query.filter_by(policy_uuid=pol_uuid).first()
                res = policy.as_dict() if policy else policy
            except Exception as e:
                raise DatabaseError(f"Couldn't read from DB {e}")
            if not res:
                raise NotFoundInDB(pol_uuid)
            return res
        else:
            raise GenericError(f" Function received no uuid")

    def get_policies(self) -> List[Dict]:
        try:
            policies = Policy.query.all()
            res = [ pol.as_dict() for pol in policies] if policies else policies
            return res
        except Exception as e:
            raise DatabaseError(f"Counldn't fetch policies from the DB. {e}")

    def add_policy(self, policy: dict):

        uuid = policy.get("uuid", None)
        name = policy.get("name", None)

        if Policy.query.filter_by(policy_uuid=uuid).first():
            raise IntegrityError(uuid)

        try:
            # Auto-increment the IDs
            policies = Policy.query.all()
            policies_ids = sorted([pol.policy_id for pol in policies])
            new_id = policies_ids[-1] + 1 if policies_ids else 1
            now = datetime.now()
            policy = Policy(policy_id=new_id,
                            policy_uuid=uuid,
                            name=name,
                            last_modification_date=now,
                            version=1)

            self.session.add(policy)
            self.session.commit()
            return 'Succeeded', 201
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't add Policy with uuid {uuid}. {e}")

    def push_policy_firewalls(self, push: dict):
        pol_uuid = push.get("policy_Uuid", None)
        firewalls_in_req = push.get("firewall_Uuids", None)

        if not any((pol_uuid, firewalls_in_req)):
            raise GenericError("No policy or firewall uuids given.")
        try:
            policy = Policy.query.filter_by(policy_uuid=pol_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't get Policy with uuid {pol_uuid}. {e}")
        if not policy:
            raise NotFoundInDB(pol_uuid)

        db_firewalls = Firewall.query.all()
        firewall_uuids = [fw.firewall_uuid for fw in db_firewalls]
        firewalls_to_add = [fw for fw in firewalls_in_req if fw in firewall_uuids]
        firewalls_not_found = [fw for fw in firewalls_in_req if fw not in firewall_uuids]

        # Pas de push si tous les firewalls ne sont pas identifiés
        if firewalls_not_found or not firewalls_to_add:
            raise GenericError("Invalid Firewall UUIDs or not found in DB.")

        try:
            for fw_uuid in firewalls_to_add:
                firewall = Firewall.query.filter_by(firewall_uuid=fw_uuid).first()
                firewall.fk_policy = policy.policy_id
            self.session.commit()
            return policy.as_dict()
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't add push policy with uuid {pol_uuid}"
                                f" on firewalls : {firewalls_in_req}. {e}")

    def delete_policy(self, pol_uuid):
        try:
            policy = Policy.query.filter_by(policy_uuid=pol_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't delete Policy with uuid {pol_uuid}. {e}")

        if not policy:
            raise NotFoundInDB(pol_uuid)

        try:
            self.session.delete(policy)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't delete Policy with uuid {pol_uuid}. {e}")


policy_context = PolicyContext()


def get_policies():
    return policy_context.get_policies()


def get_policy(uuid):
    return policy_context.get_policy(uuid)


def delete_policy(uuid):
    return policy_context.delete_policy(uuid)


def add_policy(policy: dict):
    return policy_context.add_policy(policy)


def push_policy_firewalls(push: dict):
    return policy_context.push_policy_firewalls(push)