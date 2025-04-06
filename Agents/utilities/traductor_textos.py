def get_translated_messages(language):
    messages = {
        "Spanish": {
            "IBAN_VALIDAR_MSG1": "Debes definir el receptor IBAN de la transferencia y el importe",
            "IBAN_VALIDAR_MSG2": "Debes definir el receptor IBAN de la transferencia.",
            "IBAN_VALIDAR_MSG3": "Por favor, proporciona un receptor IBAN válido para proceder con la transferencia. Por ejemplo ES0081122233445566778888",
            "IBAN_VALIDAR_MSG4": "Por favor, proporciona un importe para la transferencia",
            "IBAN_VALIDAR_MSG5": "Verificación del IBAN exitosa",
            "TAREA_REALIZADA_PROS": "Tarea realizada, quieres que prosiga con la siguiente?:",
            "SI_NO": "(Sí/No)",
            "SI":"Sí",
            "NO":"No",
            "ALGO_MAS": "Quieres algo más?",
            "NO_PROS_ALGO_MAS": "De acuerdo, no continuaré con el resto de tareas. Quieres algo más?",
            "NUEVA_CONV": "Comenzar nueva conversación",
            "NUEVA_CONV_EMP": "Nueva conversación empezada!",
            "PREGUNTA_CUALQ": "Pregúntame sobre tareas de banca y te asistiré paso a paso",
            "PROCESO_PREG_BANC": "Solo proceso preguntas bancarias. Tienes otra duda?",
            # Nuevas traducciones para el mensaje de bienvenida
            "WELCOME_MSG": "¡Bienvenido/a {name} a tu Asistente de Banco Sabadell!",
            "INTRO_TEXT": "Estoy aquí para ayudarte con tus necesidades bancarias de forma rápida y eficiente.",
            "WHAT_CAN_I_DO": "¿Qué puedo hacer por ti?",
            "TRANSFER_SUMMARY": "Realizar <strong style='color: #0079AD;'>transferencias por ti</strong>",
            "TRANSFER_TEXT": "Puedo ayudarte a realizar transferencias bancarias de manera rápida y segura.",
            "BALANCE_SUMMARY": "Darte información <strong style='color: #0079AD;'>de tu saldo</strong>",
            "BALANCE_TEXT": "Consulta el saldo de tus cuentas en cualquier momento.",
            "CARDS_SUMMARY": "Gestionar des/bloqueos e información de tus <strong style='color: #0079AD;'>tarjetas</strong>",
            "CARDS_TEXT": "Bloquea, desbloquea o consulta detalles de tus tarjetas.",
            "MOVEMENTS_SUMMARY": "<strong style='color: #0079AD;'>Analizar</strong> tus movimientos bancarios",
            "MOVEMENTS_TEXT": "Revisa y analiza tus transacciones recientes.",
            "DOUBTS_SUMMARY": "Resolver cualquier tipo de <strong style='color: #0079AD;'>dudas (tarjetas, transferencias, banca a distancia...)</strong>",
            "DOUBTS_TEXT": "Aclaro tus preguntas sobre tarjetas, transferencias, banca a distancia y más.",
            "NEWS_SUMMARY": "<strong style='color: #0079AD;'>Darte noticias actualizadas</strong> de Banco Sabadell",
            "NEWS_TEXT": "Te mantengo al día con las últimas novedades del banco.",
            "PREFERENCES_SUMMARY": "<strong style='color: #0079AD;'>Definir preferencias</strong> (estilo de respuesta, idioma, tono, agilizar transferencias)",
            "PREFERENCES_TEXT": "Personaliza el estilo de respuesta, idioma, tono o agiliza procesos.",
            "HELP_TODAY": "¿En qué puedo ayudarte hoy?"
        },
        "English": {
            "IBAN_VALIDAR_MSG1": "You must define the IBAN receptor of the transfer and the amount",
            "IBAN_VALIDAR_MSG2": "You must define the IBAN receptor of the transfer.",
            "IBAN_VALIDAR_MSG3": "Please provide a valid IBAN receptor to proceed with the transfer. For example ES0081122233445566778888",
            "IBAN_VALIDAR_MSG4": "Please provide an amount for the transfer",
            "IBAN_VALIDAR_MSG5": "IBAN verification successful",
            "TAREA_REALIZADA_PROS": "Task completed, do you want me to proceed with the next one?",
            "SI_NO": "(Yes/No)",
            "SI":"Yes",
            "NO":"No",
            "ALGO_MAS": "Do you want anything else?",
            "NO_PROS_ALGO_MAS": "Okay, I won't proceed with the remaining tasks. Do you want anything else?",
            "NUEVA_CONV": "Start New Conversation",
            "NUEVA_CONV_EMP": "New conversation started!",
            "PREGUNTA_CUALQ": "Ask me about banking tasks and I'll assist you step-by-step!",
            "PROCESO_PREG_BANC": "I only process banking requests. Do you have another doubt?",
            "WELCOME_MSG": "Welcome {name} to your Banco Sabadell Assistant!",
            "INTRO_TEXT": "I'm here to help you with your banking needs quickly and efficiently.",
            "WHAT_CAN_I_DO": "What can I do for you?",
            "TRANSFER_SUMMARY": "Perform <strong style='color: #0079AD;'>transfers for you</strong>",
            "TRANSFER_TEXT": "I can help you make bank transfers quickly and securely.",
            "BALANCE_SUMMARY": "Give you information <strong style='color: #0079AD;'>about your balance</strong>",
            "BALANCE_TEXT": "Check your account balance at any time.",
            "CARDS_SUMMARY": "Manage blocking/unblocking and information about your <strong style='color: #0079AD;'>cards</strong>",
            "CARDS_TEXT": "Block, unblock, or check details of your cards.",
            "MOVEMENTS_SUMMARY": "<strong style='color: #0079AD;'>Analyze</strong> your banking movements",
            "MOVEMENTS_TEXT": "Review and analyze your recent transactions.",
            "DOUBTS_SUMMARY": "Resolve any type of <strong style='color: #0079AD;'>doubts (cards, transfers, online banking...)</strong>",
            "DOUBTS_TEXT": "I’ll clarify your questions about cards, transfers, online banking, and more.",
            "NEWS_SUMMARY": "<strong style='color: #0079AD;'>Give you updated news</strong> from Banco Sabadell",
            "NEWS_TEXT": "I’ll keep you updated with the latest bank news.",
            "PREFERENCES_SUMMARY": "<strong style='color: #0079AD;'>Set preferences</strong> (response style, language, tone, streamline transfers)",
            "PREFERENCES_TEXT": "Customize the response style, language, tone, or streamline processes.",
            "HELP_TODAY": "How can I assist you today?"
        },
        "Catalan": {
            "IBAN_VALIDAR_MSG1": "Has de definir el receptor IBAN de la transferència i l'import",
            "IBAN_VALIDAR_MSG2": "Has de definir el receptor IBAN de la transferència.",
            "IBAN_VALIDAR_MSG3": "Si us plau, proporciona un receptor IBAN vàlid per procedir amb la transferència. Per exemple ES0081122233445566778888",
            "IBAN_VALIDAR_MSG4": "Si us plau, proporciona un import per a la transferència",
            "IBAN_VALIDAR_MSG5": "Verificació de l'IBAN exitosa",
            "TAREA_REALIZADA_PROS": "Tasca realitzada, vols que continuï amb la següent?",
            "SI_NO": "(Sí/No)",
            "SI":"Sí",
            "NO":"No",
            "ALGO_MAS": "Vols alguna cosa més?",
            "NO_PROS_ALGO_MAS": "D'acord, no continuaré amb les tasques restants. Vols alguna cosa més?",
            "NUEVA_CONV": "Començar nova conversa",
            "NUEVA_CONV_EMP": "Nova conversa començada",
            "PREGUNTA_CUALQ": "Pregunta'm sobre tasques bancàries i t'ajudaré pas a pas!",
            "PROCESO_PREG_BANC": "Solament proceso preguntes de banca. Tens un altre dubte?",
            "WELCOME_MSG": "Benvingut/da {name} al teu Assistent de Banco Sabadell!",
            "INTRO_TEXT": "Estic aquí per ajudar-te amb les teves necessitats bancàries de manera ràpida i eficient.",
            "WHAT_CAN_I_DO": "Què puc fer per tu?",
            "TRANSFER_SUMMARY": "Realitzar <strong style='color: #0079AD;'>transferències per tu</strong>",
            "TRANSFER_TEXT": "Puc ajudar-te a fer transferències bancàries de manera ràpida i segura.",
            "BALANCE_SUMMARY": "Donar-te informació <strong style='color: #0079AD;'>del teu saldo</strong>",
            "BALANCE_TEXT": "Consulta el saldo dels teus comptes en qualsevol moment.",
            "CARDS_SUMMARY": "Gestionar bloquejos/desbloquejos i informació de les teves <strong style='color: #0079AD;'>targetes</strong>",
            "CARDS_TEXT": "Bloqueja, desbloqueja o consulta detalls de les teves targetes.",
            "MOVEMENTS_SUMMARY": "<strong style='color: #0079AD;'>Analitzar</strong> els teus moviments bancaris",
            "MOVEMENTS_TEXT": "Revisa i analitza les teves transaccions recents.",
            "DOUBTS_SUMMARY": "Resoldre qualsevol tipus de <strong style='color: #0079AD;'>dubtes (targetes, transferències, banca a distància...)</strong>",
            "DOUBTS_TEXT": "Aclareixo els teus dubtes sobre targetes, transferències, banca a distància i més.",
            "NEWS_SUMMARY": "<strong style='color: #0079AD;'>Donar-te notícies actualitzades</strong> de Banco Sabadell",
            "NEWS_TEXT": "Et mantinc al dia amb les últimes novetats del banc.",
            "PREFERENCES_SUMMARY": "<strong style='color: #0079AD;'>Definir preferències</strong> (estil de resposta, idioma, to, agilitzar transferències)",
            "PREFERENCES_TEXT": "Personalitza l'estil de resposta, idioma, to o agilitza processos.",
            "HELP_TODAY": "En què puc ajudar-te avui?"
        },
        "German": {
            "IBAN_VALIDAR_MSG1": "Sie müssen den IBAN-Empfänger der Überweisung und den Betrag angeben",
            "IBAN_VALIDAR_MSG2": "Sie müssen den IBAN-Empfänger der Überweisung angeben.",
            "IBAN_VALIDAR_MSG3": "Bitte geben Sie einen gültigen IBAN-Empfänger an, um mit der Überweisung fortzufahren. Zum Beispiel ES0081122233445566778888",
            "IBAN_VALIDAR_MSG4": "Bitte geben Sie einen Betrag für die Überweisung an",
            "IBAN_VALIDAR_MSG5": "IBAN-Verifizierung erfolgreich",
            "TAREA_REALIZADA_PROS": "Aufgabe abgeschlossen, soll ich mit der nächsten fortfahren?",
            "SI_NO": "(Ja/Nein)",
            "SI":"Ja",
            "NO":"Nein",
            "ALGO_MAS": "Möchtest du noch etwas?",
            "NO_PROS_ALGO_MAS": "Okay, ich mache mit den restlichen Aufgaben nicht weiter. Möchtest du noch etwas?",
            "NUEVA_CONV": "Neue Unterhaltung starten",
            "NUEVA_CONV_EMP": "Neue Unterhaltung gestartet!",
            "PREGUNTA_CUALQ": "Frag mich nach Bankaufgaben und ich werde dir Schritt für Schritt helfen!",
            "PROCESO_PREG_BANC": "Ich bearbeite nur Bankanfragen. Hast du eine andere Frage?",
            "WELCOME_MSG": "Willkommen {name} bei deinem Banco Sabadell Assistenten!",
            "INTRO_TEXT": "Ich bin hier, um dir bei deinen Bankbedürfnissen schnell und effizient zu helfen.",
            "WHAT_CAN_I_DO": "Was kann ich für dich tun?",
            "TRANSFER_SUMMARY": "<strong style='color: #0079AD;'>Überweisungen für dich</strong> durchführen",
            "TRANSFER_TEXT": "Ich kann dir helfen, Überweisungen schnell und sicher durchzuführen.",
            "BALANCE_SUMMARY": "Dir Informationen <strong style='color: #0079AD;'>über dein Guthaben</strong> geben",
            "BALANCE_TEXT": "Überprüfe jederzeit den Kontostand deiner Konten.",
            "CARDS_SUMMARY": "Sperrung/Entsperrung und Informationen zu deinen <strong style='color: #0079AD;'>Karten</strong> verwalten",
            "CARDS_TEXT": "Sperre, entsperre oder überprüfe Details deiner Karten.",
            "MOVEMENTS_SUMMARY": "Deine Bankbewegungen <strong style='color: #0079AD;'>analysieren</strong>",
            "MOVEMENTS_TEXT": "Überprüfe und analysiere deine letzten Transaktionen.",
            "DOUBTS_SUMMARY": "Jede Art von <strong style='color: #0079AD;'>Fragen (Karten, Überweisungen, Online-Banking...)</strong> klären",
            "DOUBTS_TEXT": "Ich kläre deine Fragen zu Karten, Überweisungen, Online-Banking und mehr.",
            "NEWS_SUMMARY": "Dir <strong style='color: #0079AD;'>aktuelle Neuigkeiten</strong> von Banco Sabadell geben",
            "NEWS_TEXT": "Ich halte dich über die neuesten Nachrichten der Bank auf dem Laufenden.",
            "PREFERENCES_SUMMARY": "<strong style='color: #0079AD;'>Präferenzen festlegen</strong> (Antwortstil, Sprache, Ton, Überweisungen beschleunigen)",
            "PREFERENCES_TEXT": "Passe den Antwortstil, die Sprache, den Ton an oder beschleunige Prozesse.",
            "HELP_TODAY": "Wie kann ich dir heute helfen?"
        },
        "French": {
            "IBAN_VALIDAR_MSG1": "Vous devez définir le récepteur IBAN du virement et le montant",
            "IBAN_VALIDAR_MSG2": "Vous devez définir le récepteur IBAN du virement.",
            "IBAN_VALIDAR_MSG3": "Veuillez fournir un récepteur IBAN valide pour procéder au virement. Par exemple ES0081122233445566778888",
            "IBAN_VALIDAR_MSG4": "Veuillez fournir un montant pour le virement",
            "IBAN_VALIDAR_MSG5": "Vérification de l'IBAN réussie",
            "TAREA_REALIZADA_PROS": "Tâche effectuée, veux-tu que je passe à la suivante?",
            "SI_NO": "(Oui/Non)",
            "SI":"Oui",
            "NO":"Non",
            "ALGO_MAS": "Veux-tu autre chose?",
            "NO_PROS_ALGO_MAS": "D'accord, je ne continuerai pas avec les tâches restantes. Veux-tu autre chose?",
            "NUEVA_CONV": "Commencer une nouvelle conversation",
            "NUEVA_CONV_EMP": "Nouvelle conversation commencée !",
            "PREGUNTA_CUALQ": "Demande-moi des tâches bancaires et je t'aiderai étape par étape !",
            "PROCESO_PREG_BANC": "Je ne traite que les demandes bancaires. As-tu une autre question?",
            "WELCOME_MSG": "Bienvenue {name} chez ton Assistant Banco Sabadell !",
            "INTRO_TEXT": "Je suis ici pour t’aider avec tes besoins bancaires de manière rapide et efficace.",
            "WHAT_CAN_I_DO": "Que puis-je faire pour toi ?",
            "TRANSFER_SUMMARY": "Effectuer des <strong style='color: #0079AD;'>virements pour toi</strong>",
            "TRANSFER_TEXT": "Je peux t’aider à effectuer des virements bancaires rapidement et en toute sécurité.",
            "BALANCE_SUMMARY": "Te donner des informations <strong style='color: #0079AD;'>sur ton solde</strong>",
            "BALANCE_TEXT": "Consulte le solde de tes comptes à tout moment.",
            "CARDS_SUMMARY": "Gérer le blocage/déblocage et les informations de tes <strong style='color: #0079AD;'>cartes</strong>",
            "CARDS_TEXT": "Bloque, débloque ou consulte les détails de tes cartes.",
            "MOVEMENTS_SUMMARY": "<strong style='color: #0079AD;'>Analyser</strong> tes mouvements bancaires",
            "MOVEMENTS_TEXT": "Consulte et analyse tes transactions récentes.",
            "DOUBTS_SUMMARY": "Résoudre tout type de <strong style='color: #0079AD;'>doutes (cartes, virements, banque en ligne...)</strong>",
            "DOUBTS_TEXT": "Je clarifie tes questions sur les cartes, les virements, la banque en ligne et plus encore.",
            "NEWS_SUMMARY": "Te donner des <strong style='color: #0079AD;'>nouvelles actualisées</strong> de Banco Sabadell",
            "NEWS_TEXT": "Je te tiens au courant des dernières nouvelles de la banque.",
            "PREFERENCES_SUMMARY": "<strong style='color: #0079AD;'>Définir des préférences</strong> (style de réponse, langue, ton, accélérer les virements)",
            "PREFERENCES_TEXT": "Personnalise le style de réponse, la langue, le ton ou accélère les processus.",
            "HELP_TODAY": "Comment puis-je t’aider aujourd’hui ?"
        }
    }
    
    return messages.get(language, messages["Spanish"])  # Español por defecto si el idioma no es válido