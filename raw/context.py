"""Contexte des prochains matchs : absences importantes, équipes remaniées, matchs sans enjeu.

Rempli à chaque mise à jour (voir UPDATE.md, étape « Contexte »). Ne jamais inventer : chaque entrée cite sa source.
Clés : noms des équipes exactement comme dans raw/<championnat>.txt.
  lvl = "alerte" : le pronostic du modèle est faussé (ex. buteur et meneur du favori forfaits, équipe B alignée) ;
                   le match est retiré des paris verts, des tickets et des jackpots.
  lvl = "info"   : à savoir, sans effet sur les propositions (ex. un titulaire incertain).
"""
CHECKED_AT = "2026-11-05T03:40"   # date et heure de Paris de la dernière vérification
CONTEXT = {
    "l1": {
        ("Olympique Lyonnais", "Angers SCO"): {"lvl": "info", "why": "Lyon sans Openda (fissure du péroné).", "src": "https://m.maxifoot.fr/lyon/coup-dur-pour-openda-foot-465540.htm"},
        ("Paris", "Monaco"): {"lvl": "info", "why": "Monaco sans Ansu Fati ni Idumbo ; Dier incertain.", "src": "https://butfootballclub.fr/1708950-pronostic-paris-fc-as-monaco-01-11-prono-cotes-et-compos"},
    },
    "pl": {
        ("Liverpool", "Arsenal"): {"lvl": "alerte", "why": "Arsenal sans Saka ni Saliba (blessés), Dowman suspendu ; Liverpool sans Ekitike, Szoboszlai incertain.", "src": "https://www.sportsmole.co.uk/football/liverpool/preview/liverpool-vs-arsenal-prediction-team-news-lineups_608057.html"},
        ("Chelsea", "Manchester United"): {"lvl": "alerte", "why": "Chelsea sans João Pedro, Reece James, Lacroix, Gittens ; United sans Sesko, Ugarte, Dorgu.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
        ("Tottenham Hotspur", "Crystal Palace"): {"lvl": "alerte", "why": "Tottenham sans Xavi Simons, Bergvall, Odobert, Mudryk ; Palace sans Ismaïla Sarr.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
        ("Manchester City", "Brighton & Hove Albion"): {"lvl": "info", "why": "City sans Semenyo ; Brighton sans Mitoma ni Ferguson.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
        ("Aston Villa", "Fulham"): {"lvl": "info", "why": "Villa sans Onana, Wan-Bissaka ; Sessegnon suspendu.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
        ("Brentford", "Nottingham Forest"): {"lvl": "info", "why": "Brentford sans Carvalho, Yarmoliuk suspendu ; Forest sans Igor Jesus.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
        ("Coventry City", "Sunderland"): {"lvl": "info", "why": "Coventry sans Haji Wright ni Woolfenden.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
        ("Newcastle United", "Everton"): {"lvl": "info", "why": "Newcastle sans Livramento ; Grealish incertain.", "src": "https://dave.sport/news/premier-league-weekend-preview-team-news/"},
    },
    "liga": {
        ("FC Barcelona", "Deportivo Alavés"): {"lvl": "alerte", "why": "Barcelone sans Olmo, Koundé, Eric García ni Christensen.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
        ("Athletic Club", "Real Sociedad"): {"lvl": "alerte", "why": "Athletic sans Guruzeta ni Galarreta, Sancet incertain ; Real Sociedad sans Zakharyan.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
        ("Deportivo La Coruña", "Osasuna"): {"lvl": "alerte", "why": "La Corogne sans Aubameyang ni Casadó ; Osasuna sans Aimar Oroz ni Herrando.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
        ("Rayo Vallecano", "Celta de Vigo"): {"lvl": "info", "why": "Rayo sans son gardien Batalla ; Celta sans Borja Iglesias.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
        ("Racing Santander", "Real Madrid"): {"lvl": "info", "why": "Real Madrid sans Rodrygo ni Asencio, Valverde incertain.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
        ("Levante", "Atlético Madrid"): {"lvl": "info", "why": "Atlético : Koke et Johnny Cardoso incertains.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
        ("Real Betis", "Málaga"): {"lvl": "info", "why": "Betis sans Cucho Hernández.", "src": "https://www.futbolfantasy.com/laliga/lesionados"},
    },
    "sa": {
        ("Udinese", "Roma"): {"lvl": "alerte", "why": "Roma sans Svilar (gardien), Dybala, Pellegrini ni Koné.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("AC Milan", "Inter"): {"lvl": "alerte", "why": "Inter sans Lautaro (capitaine, buteur), Stones, Pavard ; Milan sans Tomori, Gabbia, Loftus-Cheek.", "src": "https://www.goal.com/it/liste/chi-salta-milan-inter-i-giocatori-infortunati-e-squalificati-chi-recupera-per-il-derby-di-milano/blt1cba8faa5762701b"},
        ("Como", "Venezia"): {"lvl": "alerte", "why": "Como sans Kean, Diao, Chalobah ; Venezia sans Adorante.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("Lecce", "Genoa"): {"lvl": "alerte", "why": "Lecce : Gaspar suspendu ; Pierotti, Ilic, Coulibaly, Berisha, Geubbels blessés.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("Juventus", "Napoli"): {"lvl": "alerte", "why": "Juventus sans Yildiz, Locatelli, Thuram, Conceição ; Napoli sans Lobotka, Buongiorno, Neres.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("Atalanta", "Parma"): {"lvl": "alerte", "why": "Atalanta : 9 absents dont Scamacca, Raspadori, Hien, Kessié.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("Bologna", "Monza"): {"lvl": "info", "why": "Monza sans Pessina (capitaine) ; Bologna sans Holm ni Piccoli.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("Lazio", "Cagliari"): {"lvl": "info", "why": "Lazio sans Gudmundsson.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
        ("Sassuolo", "Fiorentina"): {"lvl": "info", "why": "Sassuolo : Thorstvedt suspendu ; Fiorentina sans Ranieri ni Pongracic.", "src": "https://www.gianlucadimarzio.com/news-calcio/serie-a-probabili-formazioni-10a-giornata-498935"},
    },
    "bl": {
        ("Hamburger SV", "Borussia Mönchengladbach"): {"lvl": "alerte", "why": "Gladbach sans Kleindienst (avant-centre), Honorat ni Bolin ; HSV sans Bornauw, Capaldo, Poulsen.", "src": "https://www.sportsmole.co.uk/football/hamburger-sv/preview/hamburger-sv-vs-borussia-mbach-prediction-team-news-lineups_608398.html"},
        ("FC Bayern München", "Borussia Dortmund"): {"lvl": "alerte", "why": "Bayern sans Neuer (gardien, capitaine), Musiala ni Luis Díaz ; Kimmich incertain.", "src": "https://www.t-online.de/sport/fussball/bundesliga/fc-bayern-muenchen/id_101504822/fc-bayern-neuer-fehlt-auch-gegen-dortmund-kimmich-rueckkehr-offen.html"},
        ("Borussia Mönchengladbach", "Paderborn"): {"lvl": "alerte", "why": "Gladbach sans Kleindienst ni Honorat ; Paderborn : 5 absents.", "src": "https://bundesliga.com/en/bundesliga/news/team-news-line-ups-2026-27-bayern-dortmund-fantasy-20707"},
        ("Bayer 04 Leverkusen", "VfB Stuttgart"): {"lvl": "alerte", "why": "Leverkusen sans Terrier, Kofane, Ben Seghir ; Stuttgart sans Diehl.", "src": "https://bundesliga.com/en/bundesliga/news/team-news-line-ups-2026-27-bayern-dortmund-fantasy-20707"},
        ("Schalke 04", "RB Leipzig"): {"lvl": "info", "why": "Schalke : plusieurs absents (Gantenbein, Sylla) ; Leipzig : Nkunku incertain.", "src": "https://bundesliga.com/en/bundesliga/news/team-news-line-ups-2026-27-bayern-dortmund-fantasy-20707"},
        ("Werder Bremen", "TSG Hoffenheim"): {"lvl": "info", "why": "Brême : 7 absents dont Stage et Musah ; Hoffenheim : Prass suspendu.", "src": "https://bundesliga.com/en/bundesliga/news/team-news-line-ups-2026-27-bayern-dortmund-fantasy-20707"},
        ("FC Union Berlin", "FC Köln"): {"lvl": "info", "why": "Cologne sans Dallinga ni Skhiri ; Uduokhai suspendu.", "src": "https://bundesliga.com/en/bundesliga/news/team-news-line-ups-2026-27-bayern-dortmund-fantasy-20707"},
        ("Eintracht Frankfurt", "Hamburger SV"): {"lvl": "info", "why": "Hambourg : 6 absents dont Remberg et Vieira.", "src": "https://bundesliga.com/en/bundesliga/news/team-news-line-ups-2026-27-bayern-dortmund-fantasy-20707"},
    },
    "ucl": {
        ("Porto", "Napoli"): {"lvl": "alerte", "why": "Naples : 7 absents dont Lobotka, Di Lorenzo (capitaine), Neres et Spinazzola ; De Bruyne, Højlund et Milinković-Savić incertains.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Slavia Praha", "Arsenal"): {"lvl": "alerte", "why": "Arsenal sans Saka ni Saliba, Eze incertain ; Slavia sans Ouanda, Piták, Schranz.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Lens", "Como"): {"lvl": "alerte", "why": "Côme sans Kean ni Diao, Chalobah incertain ; Lens sans Édouard, Ganiou, Sima.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Fenerbahçe", "Liverpool"): {"lvl": "info", "why": "Liverpool sans Ekitiké, Frimpong, Bradley, Leoni ; Fenerbahçe sans Asensio ni Aké.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("AEK Athens", "Real Madrid"): {"lvl": "info", "why": "Real Madrid sans Rodrygo ni Raúl Asencio ; AEK sans João Mario, Strakosha (gardien) incertain.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("RB Leipzig", "Manchester City"): {"lvl": "info", "why": "City sans Semenyo ; Leipzig sans Ouédraogo.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Borussia Dortmund", "Real Betis"): {"lvl": "info", "why": "Betis sans Cucho Hernández ni Junior Firpo.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Villarreal", "Paris Saint Germain"): {"lvl": "alerte", "why": "PSG sans Dembélé, Kvaratskhelia, Marquinhos ni Nuno Mendes (absents du groupe).", "src": "https://www.beinsports.com/fr-fr/football/uefa-ligue-des-champions/articles/ligue-des-champions-avec-quatre-grosses-absences-le-groupe-du-psg-contre-villarreal-2026-11-02"},
        ("Atlético Madrid", "FC Bayern München"): {"lvl": "alerte", "why": "Bayern sans Luis Díaz, Musiala, Gnabry ni Saibari ; Neuer et Olise dans le groupe mais incertains. Atlético : Hjulmand suspendu, Cardoso blessé.", "src": "https://www.espn.com/soccer/story/_/id/50359298/michael-olise-rejoin-bayern-ucl-clash-atletico-madrid"},
        ("FC Barcelona", "Aston Villa"): {"lvl": "alerte", "why": "Barcelone sans Koundé, Olmo, Christensen ni Eric García.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Feyenoord", "Inter"): {"lvl": "alerte", "why": "Inter sans Lautaro Martínez, Bastoni (suspendu), Stones ni Jones ; Feyenoord : 6 absents.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
        ("Manchester United", "Roma"): {"lvl": "alerte", "why": "Roma sans Svilar (gardien), Pellegrini ni Koné, Dybala incertain ; United sans Šeško, Shaw ni Dorgu.", "src": "https://www.uefa.com/uefachampionsleague/news/02ab-21f9907f0a27-6a6a67e9775d-1000--champions-league-predicted-line-ups-matchday-4-team-news-/"},
    },
    "uel": {
        ("Milan", "Ferencváros"): {"lvl": "alerte", "why": "Milan sans Maignan (gardien, suspendu), Tomori, Gabbia, Saelemaekers, Loftus-Cheek ni Chukwueze ; rotation annoncée.", "src": "https://www.sportsmole.co.uk/football/ac-milan/europa-league/preview/ac-milan-vs-ferencvaros-prediction-team-news-lineups_608327.html"},
        ("AZ Alkmaar", "Juventus"): {"lvl": "alerte", "why": "Juventus sans Locatelli (capitaine), Yildiz, Grabara, K. Thuram, Conceição, Nico González ni Çelik.", "src": "https://www.sportsmole.co.uk/football/az/europa-league/preview/az-vs-juventus-prediction-team-news-lineups_608333.html"},
        ("Leverkusen", "Marseille"): {"lvl": "alerte", "why": "Leverkusen sans quatre attaquants (Ben Seghir, Terrier, Kofane, Diaby) ni Doué ; Marseille : Emerson incertain.", "src": "https://www.sportsmole.co.uk/football/bayer-leverkusen/europa-league/preview/b-leverkusen-vs-marseille-prediction-team-news-lineups_608338.html"},
        ("Real Sociedad", "Lyon"): {"lvl": "info", "why": "Lyon sans Tagliafico, Openda, Šulc, Morton ni Ouédraogo ; Real Sociedad sans Beitia, Odriozola, Zakharyan.", "src": "https://www.sportsmole.co.uk/football/real-sociedad/europa-league/preview/real-sociedad-vs-lyon-prediction-team-news-lineups_608324.html"},
        ("Celtic", "Beşiktaş"): {"lvl": "info", "why": "Beşiktaş sans Kökçü, Miretti ni Akdağ (suspendu), Černý incertain.", "src": "https://starting11.com/fixtures/celtic-vs-besiktas"},
        ("Sunderland", "GNK Dinamo"): {"lvl": "info", "why": "Sunderland sans ses défenseurs centraux Alderete et Danso (suspendus), ni Ballard ni Mundle.", "src": "https://starting11.com/fixtures/sunderland-vs-dinamo-zagreb"},
        ("N.E.C. Nijmegen", "Omonia"): {"lvl": "info", "why": "NEC sans Tadić, Sandler, Nuytinck, Emre Mor ni Geiger.", "src": "https://sportsmole.co.uk/football/nec/europa-league/preview/nijmegen-vs-omonia-prediction-team-news-lineups_608344.html"},
    },
    "uecl": {
        ("Atalanta", "Kairat Almaty"): {"lvl": "info", "why": "Atalanta sans Hien, Kristensen, Bellanova, Kossounou ni Gaetano ; Kessié, Kolasinac, Raspadori et Scamacca incertains.", "src": "https://www.sportsmole.co.uk/football/atalanta-bc/europa-conference-league/preview/atalanta-vs-kairat-prediction-team-news-lineups_608346.html"},
        ("Getafe", "Brighton"): {"lvl": "info", "why": "Brighton sans Mitoma, Ferguson, Tzimas, Azeez, plusieurs changements attendus ; Getafe sans Uche ni Juanmi.", "src": "https://www.sportsmole.co.uk/football/getafe/europa-conference-league/preview/getafe-vs-brighton-prediction-team-news-lineups_608340.html"},
        ("Trabzonspor", "Freiburg"): {"lvl": "info", "why": "Trabzonspor sans Malinovskyi, Okay Yokuşlu, Franculino ni Lopes Cabral (suspendu), gardien Çevikkan incertain.", "src": "https://www.sportsmole.co.uk/football/trabzonspor/europa-conference-league/preview/trabzonspor-vs-freiburg-prediction-team-news-lineups_608341.html"},
        ("Midtjylland", "Ajax"): {"lvl": "info", "why": "Ajax : Brandt très incertain, Adingra, Dolberg et Edvardsen possiblement absents ; Midtjylland : 6 absents.", "src": "https://www.sportsmole.co.uk/football/ajax/europa-conference-league/preview/midtjylland-vs-ajax-prediction-team-news-lineups_608320.html"},
        ("Twente", "Pafos"): {"lvl": "info", "why": "Twente sans son gardien Unnerstall ni Bruns ; Pafos sans son gardien Gorter ni Jaja.", "src": "https://www.sportsmole.co.uk/football/fc-twente/europa-conference-league/preview/fc-twente-vs-pafos-prediction-team-news-lineups_608352.html"},
        ("Monaco", "Nordsjælland"): {"lvl": "info", "why": "Monaco sans Ansu Fati ni Idumbo ; Nordsjælland : Janssen suspendu.", "src": "https://www.sportsmole.co.uk/football/as-monaco/europa-conference-league/preview/monaco-vs-nordsjaelland-prediction-team-news-lineups_608291.html"},
    },
}
