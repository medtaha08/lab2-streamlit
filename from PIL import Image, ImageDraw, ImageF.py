from PIL import Image, ImageDraw, ImageFont
import os

# Oracle SQL Developer color scheme
BG_COLOR = (255, 255, 255)          # white background
GUTTER_BG = (236, 236, 236)         # light grey gutter
GUTTER_BORDER = (200, 200, 200)     # gutter right border
KEYWORD_COLOR = (0, 0, 255)         # blue keywords  -> actually SQL Dev uses a medium blue
KEYWORD_COLOR = (24, 109, 190)      # SQL Dev blue
STRING_COLOR = (0, 128, 0)          # green strings
NUMBER_COLOR = (0, 128, 0)          # green numbers
NORMAL_COLOR = (0, 0, 0)            # black normal text
TYPE_COLOR = (24, 109, 190)         # blue for types after %
COMMENT_COLOR = (128, 128, 128)     # grey for comments
HIGHLIGHT_LINE = (255, 255, 220)    # yellowish highlight (last edited line)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"       # Consolas Régulier
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf" # Consolas Gras
FONT_SIZE = 22
LINE_HEIGHT = 30
GUTTER_WIDTH = 28
LEFT_PAD = 12
TOP_PAD = 8
BOTTOM_PAD = 8

PL_KEYWORDS = {
    'DECLARE','BEGIN','END','IF','THEN','ELSIF','ELSE','END IF',
    'LOOP','END LOOP','FOR','WHILE','RETURN','IS','AS','NOT',
    'NULL','RAISE','EXCEPTION','WHEN','OTHERS','OR','AND',
    'PROCEDURE','FUNCTION','TRIGGER','PACKAGE','BODY',
    'BEFORE','AFTER','INSTEAD','OF','ON','EACH','ROW','FOR EACH ROW',
    'INSERTING','UPDATING','DELETING',
    # SQL keywords
    'SELECT','FROM','WHERE','INTO','VALUES','INSERT','UPDATE','DELETE',
    'CREATE','TABLE','VIEW','SEQUENCE','OR REPLACE','PRIMARY','KEY',
    'REFERENCES','JOIN','LEFT','RIGHT','INNER','OUTER',
    'WITH','SET','GROUP BY','ORDER BY','HAVING','DISTINCT',
    'NVL','SYSDATE','NEXTVAL','CURRVAL',
    'RAISE_APPLICATION_ERROR','DBMS_OUTPUT',
    'NUMBER','VARCHAR','VARCHAR2','DATE','CHAR',
    'TYPE','ROWTYPE',
    'COMMIT','ROLLBACK','SAVEPOINT',
    'IN','OUT',
}

def tokenize(line):
    """Tokenize a PL/SQL line into (text, color, bold) tuples."""
    tokens = []
    i = 0
    s = line
    
    # Check if entire line is a comment
    stripped = s.strip()
    if stripped.startswith('--'):
        return [(s, COMMENT_COLOR, False)]
    
    while i < len(s):
        # Try to match keywords at word boundaries
        matched = False
        
        # Check for string literal
        if s[i] == "'":
            j = i + 1
            while j < len(s) and s[j] != "'":
                j += 1
            j += 1
            tokens.append((s[i:j], STRING_COLOR, False))
            i = j
            matched = True
        
        if not matched:
            # Try keyword match
            for kw in sorted(PL_KEYWORDS, key=len, reverse=True):
                end = i + len(kw)
                if s[i:end].upper() == kw:
                    # Check word boundary after
                    after = s[end] if end < len(s) else ' '
                    before = s[i-1] if i > 0 else ' '
                    if (after in ' \t;,()\n.%:' or end == len(s)) and \
                       (before in ' \t;,()\n.%:' or i == 0):
                        tokens.append((s[i:end], KEYWORD_COLOR, True))
                        i = end
                        matched = True
                        break
        
        if not matched:
            # Accumulate normal chars until next keyword/string boundary
            j = i + 1
            while j < len(s):
                if s[j] == "'":
                    break
                # peek if keyword starts here
                kw_found = False
                for kw in sorted(PL_KEYWORDS, key=len, reverse=True):
                    end = j + len(kw)
                    if s[j:end].upper() == kw:
                        after = s[end] if end < len(s) else ' '
                        before = s[j-1] if j > 0 else ' '
                        if (after in ' \t;,()\n.%:' or end == len(s)) and \
                           (before in ' \t;,()\n.%:' or j == 0):
                            kw_found = True
                            break
                if kw_found:
                    break
                j += 1
            tokens.append((s[i:j], NORMAL_COLOR, False))
            i = j
    
    return tokens


def render_code_image(code_lines, output_path, highlight_last=False):
    """Render code lines as Oracle SQL Developer screenshot."""
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    font_bold = ImageFont.truetype(FONT_BOLD_PATH, FONT_SIZE)
    
    # Measure char width
    dummy = Image.new('RGB', (1, 1))
    dd = ImageDraw.Draw(dummy)
    char_w = dd.textlength("M", font=font)
    
    # Calculate image dimensions
    max_line_len = max((len(line) for line in code_lines), default=40)
    width = GUTTER_WIDTH + LEFT_PAD + int(max_line_len * char_w) + 40
    height = TOP_PAD + len(code_lines) * LINE_HEIGHT + BOTTOM_PAD
    
    img = Image.new('RGB', (max(width, 600), height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw gutter
    draw.rectangle([0, 0, GUTTER_WIDTH - 1, height - 1], fill=GUTTER_BG)
    draw.line([(GUTTER_WIDTH, 0), (GUTTER_WIDTH, height)], fill=GUTTER_BORDER, width=1)
    
    # Draw minus sign in gutter for block starts
    block_starters = {'DECLARE', 'BEGIN', 'EXCEPTION', 'END'}
    
    for idx, line in enumerate(code_lines):
        y = TOP_PAD + idx * LINE_HEIGHT
        
        # Highlight last edited line
        if highlight_last and idx == len(code_lines) - 1:
            draw.rectangle([GUTTER_WIDTH, y, img.width, y + LINE_HEIGHT - 1], fill=HIGHLIGHT_LINE)
        
        # Draw gutter collapse icon for block starters
        stripped = line.strip()
        first_word = stripped.split()[0].upper() if stripped.split() else ''
        if first_word in block_starters or stripped.upper() in block_starters:
            # Draw small minus box
            gx = 6
            gy = y + LINE_HEIGHT // 2 - 5
            draw.rectangle([gx, gy, gx + 12, gy + 12], outline=(150, 150, 150), fill=GUTTER_BG)
            draw.line([(gx + 2, gy + 6), (gx + 10, gy + 6)], fill=(80, 80, 80), width=1)
        
        # Render code tokens
        x = GUTTER_WIDTH + LEFT_PAD
        tokens = tokenize(line)
        for text, color, bold in tokens:
            f = font_bold if bold else font
            draw.text((x, y + 4), text, font=f, fill=color)
            x += draw.textlength(text, font=f)
    
    img.save(output_path)
    return img.width, img.height


# ─── Define all code blocks for TP3 ───────────────────────────────────────────

# Image 1: CREATE TABLE Trace_Salaire
img1_lines = [
    "CREATE TABLE Trace_Salaire (",
    "    No_emp       NUMBER,",
    "    AncienSal    NUMBER(7,2),",
    "    NouveauSal   NUMBER(7,2),",
    "    Date_Modif   DATE,",
    "    Commentaire  VARCHAR(30)",
    ");",
]

# Image 2: Trigger 1.1 - historique salaires
img2_lines = [
    "CREATE OR REPLACE TRIGGER trg_historique_salaire",
    "AFTER INSERT OR UPDATE OR DELETE ON E_employe",
    "FOR EACH ROW",
    "DECLARE",
    "    v_commentaire  VARCHAR(30);",
    "    v_ancien_sal   NUMBER(7,2) := NULL;",
    "    v_nouveau_sal  NUMBER(7,2) := NULL;",
    "BEGIN",
    "    IF INSERTING THEN",
    "        v_commentaire := 'INSERT';",
    "        v_nouveau_sal := :NEW.Salaire;",
    "    ELSIF UPDATING THEN",
    "        v_commentaire := 'UPDATE';",
    "        v_ancien_sal  := :OLD.Salaire;",
    "        v_nouveau_sal := :NEW.Salaire;",
    "    ELSIF DELETING THEN",
    "        v_commentaire := 'DELETE';",
    "        v_ancien_sal  := :OLD.Salaire;",
    "    END IF;",
    "    INSERT INTO Trace_Salaire",
    "        (No_emp, AncienSal, NouveauSal, Date_Modif, Commentaire)",
    "    VALUES",
    "        (:OLD.No_emp, v_ancien_sal, v_nouveau_sal, SYSDATE, v_commentaire);",
    "END;",
    "/",
]

# Image 3: Trigger 1.2 - date entree
img3_lines = [
    "CREATE OR REPLACE TRIGGER trg_date_entree",
    "BEFORE INSERT ON E_employe",
    "FOR EACH ROW",
    "BEGIN",
    "    IF :NEW.Dt_Entree IS NULL THEN",
    "        :NEW.Dt_Entree := SYSDATE;",
    "    END IF;",
    "END;",
    "/",
]

# Image 4: Trigger 1.3 - augmentation
img4_lines = [
    "CREATE OR REPLACE TRIGGER trg_augmentation",
    "AFTER UPDATE ON E_employe",
    "FOR EACH ROW",
    "BEGIN",
    "    INSERT INTO E_augmentation",
    "        (No_emp, Ancien_Salaire, Nouveau_Salaire, Date_Augmentation)",
    "    VALUES",
    "        (:OLD.No_emp, :OLD.Salaire, :NEW.Salaire, SYSDATE);",
    "END;",
    "/",
]

# Image 5: CREATE TABLE CAT_PROD + PRODS + ARCH_PRODS
img5_lines = [
    "CREATE TABLE CAT_PROD (",
    "    NumCat       NUMBER(3)  PRIMARY KEY,",
    "    PRIXACHATMAX NUMBER(9,2),",
    "    MARGEMAX     NUMBER(7,2)",
    ");",
    "",
    "CREATE TABLE PRODS (",
    "    NumPROD   NUMBER(3)  PRIMARY KEY,",
    "    CatPROD   NUMBER(3)  REFERENCES CAT_PROD(NumCat),",
    "    PrixACHAT NUMBER(9,2),",
    "    PrixVENTE NUMBER(9,2)",
    ");",
    "",
    "CREATE TABLE ARCH_PRODS (",
    "    NumPROD      NUMBER(3),",
    "    CatPROD      NUMBER(3),",
    "    PrixAchat    NUMBER(5,2),",
    "    OldPrixVente NUMBER(3),",
    "    NewPrixVente NUMBER(3)",
    ");",
]

# Image 6: Trigger 2.1 - vérification prix vente (part 1)
img6_lines = [
    "CREATE OR REPLACE TRIGGER trg_verif_prix",
    "BEFORE UPDATE ON PRODS",
    "FOR EACH ROW",
    "DECLARE",
    "    v_margemax     CAT_PROD.MARGEMAX%TYPE;",
    "    v_prixachatmax CAT_PROD.PRIXACHATMAX%TYPE;",
    "BEGIN",
    "    SELECT MARGEMAX, PRIXACHATMAX",
    "    INTO   v_margemax, v_prixachatmax",
    "    FROM   CAT_PROD",
    "    WHERE  NumCat = :NEW.CatPROD;",
    "",
    "    IF UPDATING('PrixVENTE') THEN",
    "        IF (:NEW.PrixVENTE - :NEW.PrixACHAT) > v_margemax THEN",
    "            INSERT INTO ARCH_PRODS",
    "                (NumPROD, CatPROD, PrixAchat, OldPrixVente, NewPrixVente)",
    "            VALUES",
    "                (:NEW.NumPROD, :NEW.CatPROD, :NEW.PrixACHAT,",
    "                 :OLD.PrixVENTE, :NEW.PrixVENTE);",
    "            RAISE_APPLICATION_ERROR(-20001,",
    "                'Marge maximale depassee pour ce produit.');",
    "        END IF;",
    "        IF :NEW.PrixVENTE < :NEW.PrixACHAT THEN",
    "            RAISE_APPLICATION_ERROR(-20002,",
    "                'Prix de vente inferieur au prix d achat.');",
    "        END IF;",
    "    END IF;",
    "",
    "    IF UPDATING('PrixACHAT') THEN",
    "        IF :NEW.PrixACHAT > v_prixachatmax THEN",
    "            RAISE_APPLICATION_ERROR(-20003,",
    "                'Prix achat depasse le maximum autorise.');",
    "        END IF;",
    "    END IF;",
    "END;",
    "/",
]

# Image 7: Trigger 2.2 - calcul prix vente auto
img7_lines = [
    "CREATE OR REPLACE TRIGGER trg_calcul_prix_vente",
    "BEFORE INSERT ON PRODS",
    "FOR EACH ROW",
    "DECLARE",
    "    v_margemax CAT_PROD.MARGEMAX%TYPE;",
    "BEGIN",
    "    IF :NEW.PrixVENTE IS NULL THEN",
    "        SELECT MARGEMAX",
    "        INTO   v_margemax",
    "        FROM   CAT_PROD",
    "        WHERE  NumCat = :NEW.CatPROD;",
    "        :NEW.PrixVENTE := :NEW.PrixACHAT + v_margemax;",
    "    END IF;",
    "END;",
    "/",
]

# Image 8: Vue
img8_lines = [
    "CREATE OR REPLACE VIEW VUE_PRODS AS",
    "    SELECT cp.NumCat,",
    "           cp.PRIXACHATMAX,",
    "           p.NumPROD,",
    "           p.PrixACHAT,",
    "           p.PrixVENTE",
    "    FROM   CAT_PROD cp",
    "    JOIN   PRODS    p ON cp.NumCat = p.CatPROD;",
]

# Image 9: Séquence + Trigger INSTEAD OF
img9_lines = [
    "CREATE SEQUENCE seq_prod START WITH 1 INCREMENT BY 1;",
    "",
    "CREATE OR REPLACE TRIGGER trg_vue_prods",
    "INSTEAD OF INSERT OR DELETE ON VUE_PRODS",
    "FOR EACH ROW",
    "DECLARE",
    "    v_margemax CAT_PROD.MARGEMAX%TYPE;",
    "BEGIN",
    "    IF INSERTING THEN",
    "        IF :NEW.NumCat IS NULL THEN",
    "            RAISE_APPLICATION_ERROR(-20010,",
    "                'NumCat ne peut pas etre NULL.');",
    "        END IF;",
    "        IF :NEW.PrixACHAT IS NULL THEN",
    "            RAISE_APPLICATION_ERROR(-20011,",
    "                'PrixAchat ne peut pas etre NULL.');",
    "        END IF;",
    "        IF :NEW.PrixVENTE IS NULL THEN",
    "            SELECT MARGEMAX",
    "            INTO   v_margemax",
    "            FROM   CAT_PROD",
    "            WHERE  NumCat = :NEW.NumCat;",
    "        END IF;",
    "        INSERT INTO PRODS (NumPROD, CatPROD, PrixACHAT, PrixVENTE)",
    "        VALUES (",
    "            seq_prod.NEXTVAL,",
    "            :NEW.NumCat,",
    "            :NEW.PrixACHAT,",
    "            NVL(:NEW.PrixVENTE, :NEW.PrixACHAT + v_margemax)",
    "        );",
    "    ELSIF DELETING THEN",
    "        INSERT INTO ARCH_PRODS",
    "            (NumPROD, CatPROD, PrixAchat, OldPrixVente, NewPrixVente)",
    "        VALUES",
    "            (:OLD.NumPROD, :OLD.NumCat, :OLD.PrixACHAT,",
    "             :OLD.PrixVENTE, NULL);",
    "        DELETE FROM PRODS WHERE NumPROD = :OLD.NumPROD;",
    "    END IF;",
    "END;",
    "/",
]

# Mettez des chemins relatifs (sans le / au début)
images = [
    (img1_lines, 'oracle_img1.png'),
    (img2_lines, 'oracle_img2.png'),
    (img3_lines, 'oracle_img3.png'),
    (img4_lines, 'oracle_img4.png'),
    (img5_lines, 'oracle_img5.png'),
    (img6_lines, 'oracle_img6.png'),
    (img7_lines, 'oracle_img7.png'),
    (img8_lines, 'oracle_img8.png'),
    (img9_lines, 'oracle_img9.png'),
]

# Supprimez ou commentez la ligne os.makedirs('/home/claude/...') qui ne sert plus
# os.makedirs('/home/claude/oracle_imgs', exist_ok=True)

for lines, path in images:
    w, h = render_code_image(lines, path)
    print(f"Généré dans le dossier du script : {path} ({w}x{h})")

print("Toutes les images ont été générées avec succès !")

os.makedirs('/home/claude/oracle_imgs', exist_ok=True)
for lines, path in images:
    w, h = render_code_image(lines, path)
    print(f"Generated {path}: {w}x{h}")

print("All images generated!")