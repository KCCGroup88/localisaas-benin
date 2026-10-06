python
import streamlit as st
import requests
import json

# ==========================================
# CONFIGURATION INITIALE & VARIABLES D'API
# ==========================================
# Lecture sécurisée de votre clé secrète via les Secrets de Streamlit
if "FEDAPAY_API_KEY" in st.secrets:
    FEDAPAY_API_KEY = st.secrets["FEDAPAY_API_KEY"]
else:
    FEDAPAY_API_KEY = ""

# Configuration fixe pour votre compte
NUMERO_DESTINATION = "0197409901" 
PRIX_ABONNEMENT_FCFA = 19000  # ~29 € convertis en FCFA

# Initialisation de la session utilisateur
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ==========================================
# FONCTION DE PAIEMENT FEDAPAY (MOBILE MONEY)
# ==========================================
def generer_lien_fedapay(montant, email):
    """Génère une session de paiement FedaPay en FCFA"""
    if not FEDAPAY_API_KEY:
        # Mode Démo / Simulation si la clé secrète n'est pas encore configurée dans les secrets
        return "https://fedapay.com"
        
    url = "https://fedapay.com"
    headers = {
        "Authorization": f"Bearer {FEDAPAY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "description": "Abonnement SaaS Contenu Localisé - Plan Pro",
        "amount": montant,
        "currency": {"iso": "XOF"},
        "callback_url": "https://streamlit.app",
        "customer": {
            "email": email,
            "firstname": "Client",
            "lastname": "SaaS"
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code in :
            return response.json()["transaction"]["checkout_url"]
        else:
            st.error(f"Erreur FedaPay : {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion à l'API : {str(e)}")
        return None

# ==========================================
# INTERFACE PRINCIPALE (STREAMLIT)
# ==========================================
st.set_page_config(page_title="LocaliSaaS - Bénin", page_icon="🇧🇯", layout="wide")

# Barre latérale : Gestion du statut
st.sidebar.title("Configuration ⚙️")
if not FEDAPAY_API_KEY:
    st.sidebar.warning("⚠️ Mode Démo actif (Clé FedaPay manquante dans les Secrets)")

if st.session_state.logged_in:
    st.sidebar.write(f"Utilisateur : **{st.session_state.user_email}**")
    status = "👑 COMPTE PRO ACTIF" if st.session_state.is_pro else "⏳ PLAN GRATUIT"
    st.sidebar.info(f"Statut : {status}")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.is_pro = False
        st.rerun()
else:
    st.sidebar.warning("Veuillez vous inscrire sur la Landing Page pour tester.")

# Vérification d'un retour de paiement réussi via URL callback
query_params = st.query_params
if "payment" in query_params and query_params["payment"] == "success":
    st.session_state.is_pro = True
    st.balloons()
    st.success("Félicitations ! Votre paiement par Mobile Money a été validé. Le Plan Pro est actif !")

# ------------------------------------------
# CAS 1 : MODE LANDING PAGE (Non connecté ou Non Pro)
# ------------------------------------------
if not st.session_state.logged_in or not st.session_state.is_pro:
    st.title("🚀 Divisez votre temps de création de contenu par 10.")
    st.subheader("Multipliez votre visibilité locale au Bénin grâce à l'IA.")
    st.write("Générez instantanément des publications adaptées pour LinkedIn, Instagram et vos listes de diffusion WhatsApp Business.")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💎 Pourquoi choisir le Plan Pro ?")
        st.write("- **Générateur WhatsApp Business Débloqué** (Le canal n°1 au Bénin)")
        st.write("- **Prompts IA Marketing Avancés** (Structure AIDA, scripts vidéo complets)")
        st.write("- **Ciblage précis par ville** (Cotonou, Parakou, Porto-Novo, Abomey-Calavi...)")
        
        # Formulaire d'accès gratuit partiel
        email_input = st.text_input("Entrez votre adresse e-mail pour commencer :", placeholder="exemple@domaine.com")
        if st.button("Accéder à l'application (Mode Gratuit)"):
            if email_input:
                st.session_state.logged_in = True
                st.session_state.user_email = email_input
                st.rerun()
            else:
                st.error("Veuillez entrer un e-mail valide.")

    with col2:
        st.markdown(f"### 💳 Inscription au Plan Pro")
        st.info(f"Tarif : **{PRIX_ABONNEMENT_FCFA} XOF / mois**")
        st.write(f"Paiement sécurisé par Mobile Money. Les fonds sont configurés pour être récupérés vers votre compte.")
        
        email_pay = st.text_input("E-mail pour la facturation :", value=st.session_state.user_email, placeholder="votre-email@gmail.com")
        
        if st.button("🚀 S'abonner via Mobile Money (MTN / Moov)"):
            if email_pay:
                st.session_state.logged_in = True
                st.session_state.user_email = email_pay
                lien_paiement = generer_lien_fedapay(PRIX_ABONNEMENT_FCFA, email_pay)
                if lien_paiement:
                    st.success("Lien de paiement Mobile Money généré avec succès !")
                    st.markdown(f"[➡️ Cliquez ici pour finaliser le paiement sur FedaPay]({lien_paiement})")
            else:
                st.error("Un e-mail de facturation est obligatoire pour générer le lien de paiement.")
        
        # Option de simulation exclusive au mode démo
        if not FEDAPAY_API_KEY and st.session_state.logged_in:
            if st.button("💡 [Simuler la réussite du paiement FedaPay - Démo]"):
                st.session_state.is_pro = True
                st.balloons()
                st.rerun()

# ------------------------------------------
# CAS 2 : TABLEAU DE BORD DU SAAS DEBLOQUE (Plan Pro)
# ------------------------------------------
else:
    st.title("🏆 Tableau de Bord - Générateur de Contenu Localisé")
    st.success("Accès Pro activé avec succès via FedaPay.")
    
    # Formulaire de contextualisation
    col_secteur, col_ville = st.columns(2)
    with col_secteur:
        secteur = st.selectbox("Votre secteur d'activité :", ["Commerce / Boutique", "Immobilier", "Prestation de service / Freelance", "Artisanat / Décoration", "Autre"])
    with col_ville:
        ville = st.text_input("Ville / Localité cible au Bénin :", placeholder="Ex: Parakou, Cotonou...")

    # Zone de texte principale (Repurposing)
    texte_brut = st.text_area("Collez votre idée brute, texte de base ou descriptif produit ici :", height=150, placeholder="Ex: Nous ouvrons un nouvel espace de coworking avec une connexion haut débit stable et de l'électricité garantie 24h/24...")

    if st.button("✨ Transformer et localiser mon contenu", type="primary"):
        if texte_brut and ville:
            with st.spinner("L'IA marketing adapte votre contenu au contexte local..."):
                
                # Structures des Prompts Système injectés et formatés
                prompt_linkedin = f"CONTEXTE B2B - Ville: {ville}. Secteur: {secteur}.\nStructure AIDA. Ton professionnel et analytique.\n\nContenu généré :\n🎯 [ATTENTION] Vous cherchez à booster votre activité à {ville} ?\n💡 [INTÉRÊT] Voici comment notre solution répond précisément aux défis du secteur ({secteur})...\n🔥 [DÉSIR] {texte_brut}\n🚀 [ACTION] Discutons-en en commentaire !\n\n#Benin #{ville.replace(' ', '')} #SaaS"
                
                prompt_instagram = f"CONTEXTE VISUEL (Reels/TikTok) - Ville: {ville}.\n\n🎬 [HOOK - 0 à 3s] Stop ! Si vous êtes à {ville}, regardez bien ceci...\n🔊 [AUDIO/VOIX OFF] Vous en avez marre des interruptions ? {texte_brut}.\n🖼️ [VISUEL] Plan dynamique sur l'offre à {ville}.\n📈 [LÉGENDE] Abonnez-vous pour ne rien manquer ! 🇧🇯"
                
                prompt_whatsapp = f"CONTEXTE PROXIMITÉ (Statuts & Listes) - Bénin.\n\nBonjour ! 👋\nUne opportunité exclusive pour vous à *{ville}* dans le domaine suivant : *{secteur}*.\n\n🔹 *Quoi ?* {texte_brut}\n🔹 *Où ?* Directement chez vous à {ville}\n\n📞 Intéressé ? Répondez directement à ce message pour réserver ou contactez-nous au {NUMERO_DESTINATION} ! ✨"

                # Stockage en session
                st.session_state.res_linkedin = prompt_linkedin
                st.session_state.res_instagram = prompt_instagram
                st.session_state.res_whatsapp = prompt_whatsapp
        else:
            st.error("Veuillez remplir la zone de texte et spécifier une ville cible.")

    # Affichage des résultats par onglets
    if "res_linkedin" in st.session_state:
        st.markdown("---")
        st.subheader("📋 Vos contenus prêts à l'emploi :")
        
        tab1, tab2, tab3 = st.tabs(["💼 LinkedIn", "📸 Instagram Reels", "💬 WhatsApp Business"])
        
        with tab1:
            st.text_area("Copier le post LinkedIn :", value=st.session_state.res_linkedin, height=200)
        with tab2:
            st.text_area("Copier le script Instagram :", value=st.session_state.res_instagram, height=200)
        with tab3:
            st.text_area("Copier le message de diffusion WhatsApp :", value=st.se
