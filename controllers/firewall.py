# blablaaaaaaaaaa

from typing import Dict, List

from app import db
from models import Firewall
from exceptions import DatabaseError, IntegrityError, NotFoundInDB, GenericError


class FirewallContext:
    def __init__(self):
        # init session
        self.session = db.session

    def get_firewall(self, fw_uuid: int) -> Dict:
        if fw_uuid:
            try:
                # get firewall with id
                firewall = Firewall.query.filter_by(firewall_uuid=fw_uuid).first()
                res = firewall.as_dict() if firewall else firewall
            except Exception as e:
                raise DatabaseError(f"Couldn't read from DB {e}")
            if not res:
                raise NotFoundInDB(fw_uuid)
            return res
        else:
            raise GenericError(f" Function received no uuid")

    def get_firewalls(self) -> List[Dict]:
        try:
            # Get all firewalls
            firewalls = Firewall.query.all()
            res = [ fw.as_dict() for fw in firewalls] if firewalls else firewalls
            return res
        except Exception as e:
            raise DatabaseError(f"Counldn't fetch firewalls from the DB. {e}")

    def add_firewall(self, firewall: dict):

        uuid = firewall.get("uuid", None)
        hostname = firewall.get("hostname", None)
        ip_address = firewall.get("ipAddress", None)
        zone = firewall.get("zone", None)
        billing_status = firewall.get("billingStatus", None)
        oper_status = firewall.get("operStatus", None)
        cluster_status = firewall.get("clusterInfo", None)

        if Firewall.query.filter_by(firewall_uuid=uuid).first():
            raise IntegrityError(uuid)

        try:
            # Auto-increment the IDs
            firewalls = Firewall.query.all()
            firewall_ids = sorted([fw.firewall_id for fw in firewalls])
            new_id = firewall_ids[-1] + 1 if firewall_ids else 1

            firewall = Firewall(firewall_id=new_id,
                                firewall_uuid=uuid,
                                hostname=hostname,
                                ip_address=ip_address,
                                zone=zone,
                                billing_status=billing_status,
                                oper_status=oper_status,
                                cluster_status=cluster_status)
            self.session.add(firewall)
            self.session.commit()
            return 'Succeeded', 201
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't add Firewall with uuid {uuid}. {e}")

    def update_firewall(self, firewall: dict):

        fw_uuid = firewall.get("uuid", None)
        hostname = firewall.get("hostname", None)
        ip_address = firewall.get("ipAddress", None)
        zone = firewall.get("zone", None)
        billing_status = firewall.get("billingStatus", None)
        oper_status = firewall.get("operStatus", None)
        cluster_status = firewall.get("clusterInfo", None)

        if not fw_uuid:
            raise GenericError("No firewall uuid given.")
        if not any((hostname,
                   ip_address,
                   zone,
                   billing_status,
                   oper_status,
                   cluster_status)):

            raise GenericError("No field to modify.")
        try:
            firewall = Firewall.query.filter_by(firewall_uuid=fw_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't get Firewall with uuid {fw_uuid}. {e}")

        if not firewall:
            raise NotFoundInDB(fw_uuid)

        try:
            if hostname:
                firewall.hostname = hostname
            if ip_address:
                firewall.ip_address = ip_address
            if zone:
                firewall.zone = zone
            if billing_status:
                firewall.billing_status = billing_status
            if oper_status:
                firewall.oper_status = oper_status
            #if fk_manager:
            #    firewall.fk_manager = fk_manager
            if cluster_status:
                firewall.cluster_status = cluster_status
            #if fk_status:
            #    firewall.fk_status = fk_status
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't update Firewall with uuid {fw_uuid}. {e}")

    def delete_firewall(self, fw_uuid):
        try:
            firewall = Firewall.query.filter_by(firewall_uuid=fw_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't delete Firewall with uuid {fw_uuid}. {e}")

        if not firewall:
            raise NotFoundInDB(fw_uuid)

        try:
            self.session.delete(firewall)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't delete Firewall with uuid {fw_uuid}. {e}")


firewall_context = FirewallContext()

def get_firewalls():
    #breakpoint()
    return firewall_context.get_firewalls()


def get_firewall(uuid):
    return firewall_context.get_firewall(uuid)


def delete_firewall(uuid):
    return firewall_context.delete_firewall(uuid)


def add_firewall(firewall: dict):
    return firewall_context.add_firewall(firewall)


def update_firewall(firewall: dict):
    return firewall_context.update_firewall(firewall)