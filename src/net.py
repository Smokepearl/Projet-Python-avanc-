"""Petit utilitaire réseau commun.

Sur certains réseaux (proxy d'entreprise faisant de l'inspection TLS), la
vérification de certificat de ``requests`` échoue car le certificat racine du
proxy n'est pas dans le magasin de ``certifi``. Le paquet ``truststore`` fait
utiliser à Python le magasin de certificats du système d'exploitation, ce qui
résout proprement le problème — sans désactiver la vérification TLS.

L'activation est silencieuse et optionnelle : si ``truststore`` n'est pas
installé (machine personnelle classique), on ne fait rien et tout fonctionne.
"""

from __future__ import annotations


def enable_system_trust_store() -> bool:
    """Active le magasin de certificats du système si ``truststore`` est dispo."""
    try:
        import truststore

        truststore.inject_into_ssl()
        # Avec truststore + urllib3, un avertissement « InsecureRequestWarning »
        # cosmétique peut apparaître bien que la vérification se fasse via le
        # magasin du système. On le masque pour garder une sortie propre.
        try:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:  # noqa: BLE001
            pass
        return True
    except Exception:  # noqa: BLE001 - purement optionnel
        return False


# Activation à l'import du package.
enable_system_trust_store()
