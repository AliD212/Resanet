#!/usr/bin/python3
# -*- coding: utf-8 -*-

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet

app = Flask(__name__)
app.secret_key = 'resanet'

@app.route('/', methods=['GET'])
def index():
    return render_template('vueAccueil.html')

@app.route('/usager/session/choisir', methods=['GET'])
def choisirSessionUsager():
    return render_template('vueConnexionUsager.html', carteBloquee=False, echecConnexion=False, saisieIncomplete=False)

@app.route('/usager/seConnecter', methods=['POST'])
def seConnecterUsager():
    numeroCarte = request.form['numeroCarte']
    mdp = request.form['mdp']

    if numeroCarte and mdp:
        usager = modeleResanet.seConnecterUsager(numeroCarte, mdp)
        if usager and usager['activee']:
            session['numeroCarte'] = usager['numeroCarte']
            session['nom'] = usager['nom']
            session['prenom'] = usager['prenom']
            session['mdp'] = mdp
            return redirect('/usager/reservations/lister')

    return render_template('vueConnexionUsager.html', carteBloquee=bool(usager and not usager['activee']), echecConnexion=not usager, saisieIncomplete=not numeroCarte or not mdp)

@app.route('/usager/seDeconnecter', methods=['GET'])
def seDeconnecterUsager():
    session.pop('numeroCarte', None)
    session.pop('nom', None)
    session.pop('prenom', None)
    return redirect('/')

@app.route('/usager/reservations/lister', methods=['GET'])
def listerReservations():
    tarifRepas = modeleResanet.getTarifRepas(session['numeroCarte'])
    soldeCarte = modeleResanet.getSolde(session['numeroCarte'])
    solde = '%.2f' % soldeCarte

    aujourdhui = datesResanet.getDateAujourdhuiISO()
    datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
    datesResas = modeleResanet.getReservationsCarte(session['numeroCarte'], datesPeriodeISO[0], datesPeriodeISO[-1])

    dates = []
    for uneDateISO in datesPeriodeISO:
        uneDate = {'iso': uneDateISO, 'fr': datesResanet.convertirDateISOversFR(uneDateISO)}

        if uneDateISO <= aujourdhui:
            uneDate['verrouillee'] = True
        else:
            uneDate['verrouillee'] = False

        if uneDateISO in datesResas:
            uneDate['reservee'] = True
        else:
            uneDate['reservee'] = False

        if soldeCarte < tarifRepas and not uneDate['reservee']:
            uneDate['verrouillee'] = True

        dates.append(uneDate)

    soldeInsuffisant = soldeCarte < tarifRepas
    dateJour = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    
    return render_template('vueListeReservations.html', laSession=session, leSolde=solde, lesDates=dates, soldeInsuffisant=soldeInsuffisant, date=dateJour)



@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ):
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
		modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
		modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
		return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )

	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route('/usager/mdp/modification/appliquer', methods=['POST'])
def modifierMdpUsager():
    ancienMdp = request.form['ancienMDP']
    nouveauMdp = request.form['nouveauMDP']

    soldeCarte = modeleResanet.getSolde(session['numeroCarte'])
    solde = '%.2f' % soldeCarte

    if ancienMdp != session['mdp'] or nouveauMdp == '':
        return render_template('vueModificationMdp.html', laSession=session, leSolde=solde, modifMdp='Erreur: Veuillez remplir tous les champs et vérifier votre ancien mot de passe')

    modeleResanet.modifierMdpUsager(session['numeroCarte'], nouveauMdp)
    session['mdp'] = nouveauMdp

    return render_template('vueModificationMdp.html', laSession=session, leSolde=solde, modifMdp='Le mot de passe a été modifié avec succès')



@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	return render_template('vueConnexionGestionnaire.html' , echecConnexion=False, saisieIncomplete=False)

@app.route('/gestionnaire/seConnecter', methods=['GET'])
def seConnecterGestionnaire():


    return render_template( 'vueFontaine.html' )
    








if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
