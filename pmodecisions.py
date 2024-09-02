import streamlit as st
import boto3
import json
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

header_html = """
    <div style="display: flex; align-items: center; padding: 10px;">
        <img src="https://eladsoft.com/wp-content/uploads/2022/03/ELAD-DATA-LOGO.png" style="width: 300px; height: 150; margin-right: 10px;">
        <h1 style="margin: 0;">משרד ראש הממשלה - פירוק החלטות למשימות</h1>
    </div>
"""
# Use st.markdown to render the HTML
st.markdown(header_html, unsafe_allow_html=True)
configure()
# Initialize the Boto3 client with the provided credentials
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id=os.getenv('id'),
    aws_secret_access_key=os.getenv('secret') 
)

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("הזן תוכן החלטת ממשלה"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

 
    system_prompt = """"
Human: You work in the Prime Minister's office in the department where the government's decisions are divided into tasks, and assigned to relevant ministries and bodies.
    From the wording of the decision, your task is to identify the tasks, in a concise and clear way, and finally to assign them to the relevant party for execution.
    Here is the text:
    """
   
    # Example tasks and references
    example_tasks ="""
    Input:להט אזורי להכין תוכנית מפורטת ופיתוח תשתיות להקמת מרכז לכנסים ומחקר שעניינו שיקום נהרות באזורים צחיחים ושמירת הנוף ומתנות הטבע, במרחב שבין נהריים לגשר הישנה. משרד החוץ בשיתוף עם המשרד לשיתוף פעולה אזורי יפעלו לתיאום הפרויקט מול שלטונות ממלכת ירדן. לצורך כך, יקצה המשרד לשיתוף פעולה אזורי סכום של 1.5 מלש"ח מתקציב 2022.
    Correct action-item: המשימה: להקצות 1.5 מלש"ח בשנת 2022 לצורך הכנת תוכנית מפורטת ופיתוח תשתיות להקמת מרכז לכנסים ומחקר שעניינו שיקום נהרות באזורים צחיחים ושמירת הנוף ומתנות הטבע, במרחב שבין נהריים לגשר הישנה.
   
    Input:להקים צוות בין-משרדי בהובלת המשרדים לשיתוף פעולה אזורי, המשרד להגנת הסביבה  ומשרד החוץ, בהשתתפות משרד החקלאות ופיתוח הכפר, משרד התיירות, משרד האנרגיה ורשות המים. הצוות יבחן פעולות נוספות לקידום שיתוף הפעולה עם ממלכת ירדן באגן נהר ירדן דרומי על ההיבטים המשותפים בין המדינות בהקשר הנהר וסביבתו הקרובה בתחומים כגון: שימור שיקום ופיתוח מי הנהר, שימור ושיקום גדות הנהר, מניעת והפחתה של נזקי שינויי אקלים, פיתוח שיתוף הפעולה בין הקהילות החיות משני עברי הנהר בתחום הכלכלי, העברת ידע ופיתוח התיירות. הצוות יפעל בהתייעצות עם המועצה האזורית עמק המעיינות והמועצה האזורית עמק הירדן ורשות ניקוז ירדן דרומי ויגיש את המלצותיו לשרים בתוך שנה. התיאום מול ירדן ייעשה בהובלת משרד החוץ, רשות המים והמשרד לשיתוף פעולה אזורי בערוצים הרלוונטיים, לרבות במסגרת תת הוועדה של ועדת המים.
    Correct action-item:המשימה: להכין תוכנית מפורטת ופיתוח תשתיות להקמת מרכז לכנסים ומחקר שעניינו שיקום נהרות באזורים צחיחים ושמירת הנוף ומתנות הטבע, במרחב שבין נהריים לגשר הישנה.
   
    Input:להטיל על המשרד להגנת הסביבה, בשיתוף משרד החקלאות ופיתוח הכפר, לבנות מודל לניהול השטחים הפתוחים באגן נהר הירדן הדרומי בתוך 6 חודשים.
    Correct action-item:המשימה: לבנות מודל לניהול השטחים הפתוחים באגן נהר הירדן הדרומי בתוך 6 חודשים.
   
    Input:הטיל על המשרד להגנת הסביבה, בתיאום עם משרד החקלאות ופיתוח הכפר, לנטר באופן רציף את מוקדי הפלט מהמדגים לנחלים. לצורך כך יקצה המשרד להגנת הסביבה 500 אלש"ח מתקציב 2022.
    Correct action-item:המשימה: להקצות 0.5 מלש"ח בשנת 2022 לצורך ניטור רציף של מוקדי הפלט מהמדגים לנחלים.
   
    Input:גיבוש תוכנית אקלים אזורית לשיקום ופיתוח אזור מורד הירדן והירדן הדרומי
    להטיל על המשרד להגנת הסביבה, בתיאום עם משרד האנרגיה ורשות המים ובהתייעצות עם משרד החקלאות ופיתוח הכפר, משרד התיירות, המשרד לשיתוף פעולה אזורי, משרד החוץ, רשות הטבע והגנים, רשויות הניקוז והנחלים והרשויות המקומיות הרלוונטיות, לגבש תוכנית אקלים אזורית לשיקום ופיתוח אזור מורד הירדן והירדן הדרומי, שתותאם, בין היתר, לתוכנית המובל המזרחי שאישרה מועצת רשות המים כאמור בסעיף 1(א) ובהתאם ליעד הקבוע בסעיף 1(ב) לעיל (להלן - התוכנית), בתוך שנה מאישור ההחלטה. מימוש היעד יהיה בהתאם לאישור התוכנית על ידי הממשלה ובכלל זאת הקצאת המשאבים הנדרשים למימושה.
    Correct action-item:המשימה: לגבש תוכנית אקלים אזורית לשיקום ופיתוח אזור מורד הירדן והירדן הדרומי, שתותאם, בין היתר, לתוכנית המובל המזרחי שאישרה מועצת רשות המים כאמור בסעיף 1(א) ובהתאם ליעד הקבוע בסעיף 1(ב) לעיל, בתוך שנה מאישור
   
    Input:המשרד לשיתוף פעולה אזורי, בתיאום עם משרד החוץ, משרד הכלכלה והתעשייה והצוות המשותף, יגבש תוכנית לקידום השקעות במיזם. המשרד לשיתוף פעולה אזורי, יחד עם משרד הכלכלה והתעשייה, יחשפו את התוכנית לתעשייה הישראלית ולמשקיעים בין-לאומיים בשילוב תוכנית הסברתית מלווה.
    Correct action-item:המשימה: לחשוף את התוכנית לתעשייה הישראלית ולמשקיעים בין-לאומיים בשילוב תוכנית הסברתית מלווה
   
    Input:המשרד לשיתוף פעולה אזורי, בתיאום עם משרד החוץ, משרד הכלכלה והתעשייה והצוות המשותף, יגבש תוכנית לקידום השקעות במיזם. המשרד לשיתוף פעולה אזורי, יחד עם משרד הכלכלה והתעשייה, יחשפו את התוכנית לתעשייה הישראלית ולמשקיעים בין-לאומיים בשילוב תוכנית הסברתית מלווה.
    Correct action-item:המשימה: לגבש תוכנית לקידום השקעות במיזם.
   
    Input:סכום של 12.5 מלש"ח יאוגם באופן מיידי בתקציב המשרד לשיתוף פעולה אזורי (להלן - "תקציב לפעולות מיידיות") מתקציבי משרד התחבורה והבטיחות בדרכים (סעיף 79 לתקציב הפיתוח של משרד התחבורה והבטיחות בדרכים) ומתקציבי משרד החוץ, משרד הכלכלה והתעשייה, המשרד לשיתוף פעולה אזורי ומשרד ראש הממשלה (2.5 מלש"ח מכל אחד מהמשרדים) לצורך מימון הפעולות הבאות: עד 3 מלש"ח יוקצו לצורך הבאת תשתיות העל לראש השטח של מסוף הפארק.
    Correct action-item:המשימה: לנצל עד 3 מלש"ח בשנת 2022 לצורך הבאת תשתיות העל לראש השטח של מסוף הפארק.
   
    Input:מימון והקצאת משאבים:
    א.    סכום של 12.5 מלש"ח יאוגם באופן מיידי בתקציב המשרד לשיתוף פעולה אזורי (להלן - "תקציב לפעולות מיידיות") מתקציבי משרד התחבורה והבטיחות בדרכים (סעיף 79 לתקציב הפיתוח של משרד התחבורה והבטיחות בדרכים) ומתקציבי משרד החוץ, משרד הכלכלה והתעשייה, המשרד לשיתוף פעולה אזורי ומשרד ראש הממשלה (2.5 מלש"ח מכל אחד מהמשרדים) לצורך מימון הפעולות הבאות:
    1)    עד 3 מלש"ח לצורך תכנון מפורט ותכנון סטטוטורי של מסוף הפארק.
    Correct action-item:המשימה: לנצל עד 3 מלש"ח בשנת 2022 לצורך תכנון מפורט ותכנון סטטוטורי של מסוף הפארק.
 
    Input: המשימה: ליישם את ההחלטה בכפוף לכל דין, לרבות דיני המכרזים.
   הגורם האחראי: כל הגורמים הרלוונטיים  
   Correct action-item: This action item has to be ignored, as it's using 'ליישם...' and it's very general one, this is an example for tasks we ignore.

   Input:3. לרשום את הודעת משרד התחבורה והבטיחות בדרכים, כי לטובת שלב תכנון התוכנית לחיבור ישראל יוקצו, באופן חד פעמי מתקציב משרד התחבורה, 70 מלש"ח בשנת 2023 ו-130 מלש"ח בשנת 2024.  
   Correct action-item:המשימה: להקצות באופן חד פעמי 130 מלש"ח בשנת 2024 לטובת שלב תכנון התכנית לחיבור ישראל.
    """
    example_fullActionItems = """"
Here, I'll put full examples, the decision and all the tasks that were given, read those examples carefully and learn. Also a note, these tasks do not have indexes and references, its just the task.
Input:
נושא ההחלטה:
צעדים למיצוי פוטנציאל התעסוקה במשק
מחליטים:
1. בהמשך לצעדים למען הגדלת הפריון והצמיחה הכלכלית במשק ונוכח החשיבות הלאומית שרואה הממשלה בהגדלת שיעורי התעסוקה של גברים חרדים כחלק מהצעדים למיצוי פוטנציאל התעסוקה במשק ובהמשך להחלטת הממשלה מס' 198 מיום 1.8.2021 (להלן - החלטת הממשלה) ועל מנת לעמוד ביעד התעסוקה לשנת 2030 של גברים חרדים כפי שנקבעו בהחלטת הממשלה:
א. להנחות את משרד העבודה (להלן - המשרד) להרחיב ולפתח תוכניות תעסוקה שונות לגברים חרדים בדגש על עידוד ותמרוץ רכישת השכלה והכשרה איכותית לשילוב בתעסוקה בשכר גבוה ובפרט:
1. רכישת השכלת בסיס באמצעות סבסוד הלימודים ופיתוח תכנים מונגשים דיגיטלית.
2. הגברת השילוב בהשכלה על-תיכונית איכותית רלוונטית לשוק העבודה ולמערכת הביטחון באמצעות תוכניות הכשרה, תמיכה וליווי באופן שיועדפו תוכניות עם תשואה גבוהה להשכלה ותרומה לצורכי מערכת הביטחון.
3. הרחבת התמיכה במהלך הלימודים על ידי מנגנון הלוואות מותנות הכנסה, כאשר הקצאת ההלוואות תהא תוך העדפה להכשרות עם תשואה גבוהה מוכחת להשכלה.
ב. המשרד יגבש תוכנית עבודה מפורטת, בתיאום עם השותפים הרלוונטיים, הכוללת מדדי תפוקה ויעדי השכלה ושכר, אשר תאושר בהסכמת אגף התקציבים במשרד האוצר ובמידת הצורך בתיאום או התייעצות עם שותפים נוספים רלוונטיים. כלי הפעולה ואופן הקצאת התקציב ליישום התוכנית על מרכיביה ייקבעו במסגרת גיבוש התוכנית. התוכנית תוצג לעיון ולהתייחסות הרשות לפיתוח כלכלי חברתי של המגזר החרדי. המשרד, בתיאום עם אגף התקציבים במשרד האוצר, יהיה רשאי לבצע התאמות והסטות בין כלי הפעולה בתוך המשרד או בין משרדי הממשלה ויחידות הסמך הרלוונטיים.
ג. בהתאם לחוק יסודות התקציב, התשמ"ה-1985 ולצורך יישום ומימון החלטה זו, להקצות סך של  70 מלש"ח מתוך סכומים ששוריינו בחוק התקציב הנוסף לשנת 2024 שיועדו לטובת החלטת הממשלה בעניין תעסוקת גברים חרדים בשנת 2024.
2. משרד העבודה יבחן את הצורך בקידום החלטת ממשלה ייעודית בנוגע לתוכניות המופעלות על ידיו לקידום תעסוקה של אנשים עם מוגבלות  בשים לב לייעד התעסוקה לאוכלוסייה זו בהחלטת הממשלה.
Tasks:
המשימה: להקצות סך של  70 מלש"ח מתוך סכומים ששוריינו בחוק התקציב הנוסף לשנת 2024 שיועדו לטובת החלטת הממשלה בעניין תעסוקת גברים חרדים בשנת 2024.
המשימה: לפנות אל מבקר המדינה, נשיא המדינה וכנסת ישראל, בבקשה להפחית את מספר העובדים, רכיבי השכר והיקף תקציבי השכר.
המשימה: המשרד יגבש תוכנית עבודה מפורטת, בתיאום עם השותפים הרלוונטיים, הכוללת מדדי תפוקה ויעדי השכלה ושכר, אשר תאושר בהסכמת אגף התקציבים במשרד האוצר ובמידת הצורך בתיאום או התייעצות עם שותפים נוספים רלוונטיים
המשימה: להחיל את האמור בסעיף 1 להחלטה זו על שירות התעסוקה ולהפחית את מספר העובדים, רכיבי השכר הנלווים, והיקף תקציבי השכר.
המשימה: לבחון את הצורך בקידום החלטת ממשלה ייעודית בנוגע לתוכניות המופעלות על ידיו לקידום תעסוקה של אנשים עם מוגבלות  בשים לב לייעד התעסוקה לאוכלוסייה זו בהחלטת הממשלה.
המשימה: להפחית את בסיס התקציב של שירות התעסוקה בשנים 2023 ואילך בהתאם לשיעורי ההפחתה האמורים בסעיף 2 להחלטה זו.
המשימה: להחיל את האמור בסעיף 1 להחלטה זו על המוסד לביטוח לאומי ולהפחית את מספר העובדים, את רכיבי השכר הנלווים ואת היקף תקציבי השכר.
המשימה: להנחות את משרד העבודה להרחיב ולפתח תוכניות תעסוקה שונות לגברים חרדים בדגש על עידוד ותמרוץ רכישת השכלה והכשרה איכותית לשילוב בתעסוקה בשכר גבוה
המשימה: להפחית את בסיס התקציב המינהלי של המוסד לביטוח לאומי בשנים 2023 ואילך בהתאם לשיעורי ההפחתה האמורים בסעיף 2 להחלטה זו.
המשימה: להחיל את האמור בסעיף 1 על עובדי הוראה המועסקים בשכר ישיר ובשכר עקיף במשרד החינוך בהשכלה גבוהה.
"""
   
    example_reference ="""
    Input:6.    מימון והקצאת משאבים:
    א.    סכום של 12.5 מלש"ח יאוגם באופן מיידי בתקציב המשרד לשיתוף פעולה אזורי (להלן - "תקציב לפעולות מיידיות") מתקציבי משרד התחבורה והבטיחות בדרכים (סעיף 79 לתקציב הפיתוח של משרד התחבורה והבטיחות בדרכים) ומתקציבי משרד החוץ, משרד הכלכלה והתעשייה, המשרד לשיתוף פעולה אזורי ומשרד ראש הממשלה (2.5 מלש"ח מכל אחד מהמשרדים) לצורך מימון הפעולות הבאות:
    Correct index as a reference:סעיף בהחלטה: 6.א
   
    Input: 7.    המשרד לשיתוף פעולה אזורי, בתיאום עם משרד החוץ, משרד הכלכלה והתעשייה והצוות המשותף, יגבש תוכנית לקידום השקעות במיזם. המשרד לשיתוף פעולה אזורי, יחד עם משרד הכלכלה והתעשייה, יחשפו את התוכנית לתעשייה הישראלית ולמשקיעים בין-לאומיים בשילוב תוכנית הסברתית מלווה.
    Correct index as a reference:סעיף בהחלטה: 7
    """
   
    instructions = """
    1. Start every action item with המשימה:
    2. At the end of every action item, refer to the index from the decision in ()
    3. After mentioning the index, mention the relevant government or minister to be in charge of the task in ()
    4. Follow the key insturctions below, make sure to read it carefully, and apply it in hebrew in all decision received.
    """
    key_instructions = """
The methodology for breaking down government decisions in the system is described deeply below, these instructions are key instructions, make sure it read it very carefully and apply it to every text recevied:
 
1.Overview:
Two main rules for dissolving government decisions
1. A task in the system is only one action, at one reporting time, by one reporting agent.
2. The original wording of the government's decision must be adhered to as much as possible, except for changes necessary for a clear wording that is consistent with the dissolution methodology.
 
2.The decomposition methodology
**1. Defining the Responsible Party for Reporting**
a. If there are multiple responsible parties for reporting on a specific task in a government decision, separate the tasks according to the number of responsible reporting parties (For example: Ministry X and Ministry Y will appoint representatives on their behalf for the matter – in such a case, create two separate tasks, i.e., one task for each ministry).
b. The default in determining the responsible party for reporting is the ministry's Director General (whose minister is responsible for carrying out the task), unless another party is explicitly stated as responsible for reporting (for example: the head of a subsidiary unit under the minister).
c. If one party needs to perform the action multiple times over several years, separate it into multiple tasks according to the different reporting years (For example: a budget transferred annually between 2021-2023 will be separated into three different tasks for each year).
d. If a single action involves multiple parties, but one party is clearly responsible for the execution, it's possible to write only one task for which this party is responsible for reporting.
   i. The rule of thumb for defining the responsible party for reporting in this case is the party that appears first in the order of parties.
   ii. For example: In an action to establish a committee (to establish a steering committee headed by Ministry X with the participation of ministries...), only the chairperson will be responsible for convening it, not all committee participants.
 
3. Formulating the Task
a. Stick to the source as closely as possible, except for making the necessary changes in the breakdown methodology (for example: when the task spans over several years - see section 2d. below).
b. Write the task in an actionable language by using the infinitive form (to establish, to transfer, etc.), without including the responsible party in the task wording (no need to write "to impose on the minister...").
c. If a specific deadline for completing the task is mentioned in the decision text, incorporate it into the task wording (for example: within 60 days from the date of this decision). In such cases, update the "target date for completion" accordingly (see section 3b. below).
d. When a task repeats itself over several years, include the year in the wording of each task (for example: to transfer 2 million NIS in 2021 for...; to transfer 2 million NIS in 2022 for... etc.).
 
4. Defining Task Execution and Reporting Deadlines**
**A. When no specific deadline for task execution is mentioned in the decision:**
i. For government decisions made between January and September, set December 31st of the same year as the deadline.
ii. For government decisions made between October and December, set December 31st of the following year as the deadline.
iii. This means the "execution deadline" and the "final reporting date" will be the same.
 
**B. When a specific deadline for task execution is mentioned in the decision:**
i. The specific task execution deadline ("execution deadline") will be defined according to the date specified in the decision.
ii. The task reporting deadline ("final reporting date") will be defined as per section 3A: if the execution deadline falls between January and September, the reporting date will be set to the end of that year (December 31st); if the execution deadline falls between October and December, the reporting date will be set to the end of the following year (December 31st).
iii. In this case, the "execution deadline" and the "final reporting date" will not be the same.
 
**C. For budgetary tasks (see section 4 below), both execution and reporting deadlines will be set to the end of the relevant fiscal year (December 31st), unless otherwise specified in the decision.
 
**D. Technical Note: Saving in the system is based on the execution date, so for tasks with different execution and reporting dates, first set the execution date, save the change, and only then set the reporting date.
 
5. Budgetary Tasks
**A.** We distinguish between three types of budgetary tasks:
1. **Allocation** of budget for an activity (allocate Y million shekels in 2023 for the activity).
2. **Transfer** of budget between entities (transfer Y million shekels in 2023 to department X for the activity).
3. **Utilization** of the total budget for an activity (utilize Y million shekels in 2023 for the activity).
 
**B.** Under the "Budget" tab, mark the budget action and complete the following data:
i. **Amount of budget transferred in the task** – write the amount of the budget in millions of shekels (e.g., if it states 2 million shekels, write 2; if it states 300,000 shekels, write 0.3). Additionally, in the task text, write "million shekels" and not "million NIS," "thousands of NIS," etc.
ii. **Type of budget task** – define the type of budget task: transfer, allocation, or utilization.
iii. **Source of the budget transferred in the task** – define whether the budget source is from ministry resources, another ministry's resources, or additional funds.
 
**C.** The reporting method will be as follows:
i. **Allocation** – when a certain ministry allocates from its own budget for a specific activity.
   - In this case, the budget source will be defined as "ministry resources."
ii. **Transfer** – when a certain ministry transfers funds to another ministry.
   - When the Budget Division (BD) transfers funds to another ministry, the budget source will be defined as "additional."
   - For any other fund transfers between ministries, the budget source will be defined as "ministry resources."
iii. **Utilization** – when a certain ministry utilizes the total amount transferred to it from other ministries for a specific activity.
   - When the ministry utilizes a budget transferred to it solely by the BD, the budget source will be defined as "additional."
   - In any other case, the budget source will be defined as "another ministry's resources."
   - Note: In the utilization action, only the total budget transferred to the ministry (from BD and/or other ministries) is included, and the amount allocated for the activity by the ministry itself is not included (see further details in example 5 under Annex B).
iv. As mentioned, selecting "additional" as the source of the budget transferred in the task will only be done when the BD is the entity transferring/allocating the budget.
v. Other transfer and allocation tasks will be marked as "ministry resources" or "another ministry's resources," as detailed above.
**E. Action with Equal Budget Distribution Over Time** – When a decision states that the budget should be allocated "equally" or "evenly," calculate the annual budget allocated for the activity according to the number of years mentioned in the task, and create a separate task for each year.
   - For example: "Allocate 20 million shekels evenly between the years 2022 – 2025" – create four tasks with an allocation of 5 million shekels for each year.
 
**F. Action Without Equal Budget Distribution Over Time** – When there is no equal distribution of the budget between the years, and there is only a general allocation for a long period, create only one task where both the execution and reporting deadlines refer to the end of the last year mentioned in the task.
   - For example: "Allocate 40 million shekels for the years 2022 – 2025, according to the ministry’s work plan" – create one task with both execution and reporting deadlines set for December 31, 2025.
 
6. Additional Notes
 
**A.** Only create actionable tasks, i.e., those that can be reported as "completed" or "not completed."
 
**B.** For general tasks ("to apply...","to promote...", "to examine...", "to act to...","to determine...","will be entitled to...", etc.), use discretion: sometimes they may be too general and not necessary to create in the system, while other times they can be considered actionable tasks. For example, if it says "act to complete...", it can usually be changed to "complete..." and treated as an actionable task.
 
**C.** It is important to distinguish between an actionable task and a general principle/guideline or a stage in a methodological process. Generally, principles, guidelines, and stages in a process are not actionable tasks.
 
**D.** Legislation and amendments to laws are not tasks, as these are carried out by the Knesset. However, amending regulations is done by government ministers and thus constitutes a task. Additionally, if a minister/department is tasked with submitting a bill for Knesset approval, these cases should also be considered tasks.
"""
 
    decision_type = """
In the following part, I'll put the classifications to the decisions, do not add it to the action-items output, but classify it to understand which action-items to present and which to ignore:
**Type of Decision (Each decision will have one primary type and several subtypes assigned)**
 
Track only decisions of types Executive, Process, and Government.
 
1. **Executive Decision** (Decisions dealing with the implementation of government policy in any field, whether through direct actions, reallocating resources within and outside the government, using economic tools to achieve policy objectives, or regulating a specific field). Code: Executive.
2. **Declarative Decision** (Decisions primarily outlining government policy, setting principles or goals, or summarizing a review or report provided to the government - which do not impose executive responsibility on any government entity). Code: Declarative.
3. **Process-Initiating Decision** (Decisions assigning responsibility to a single entity or working group to formulate policy or recommendations on a specific issue by a deadline, within a governmental framework or involving non-governmental entities). Code: Process.
4. **Appointment Decision** (Decisions concerning appointments within the government and public service, including appointments of ministers and directors-general, extensions of existing appointments, and appointments to statutory corporations and public councils, without changing government operations). Code: Appointments.
5. **Government Operations Decision** (Including appointment procedures in public service, establishing permanent work frameworks at the ministerial or professional levels, transferring and delegating powers, creating and dissolving governmental bodies, procurement, and HR procedures, etc.). Code: Government.
6. **Formal Approval Decision** (Formal approvals required by law for decisions by bodies and boards, approval of government company budgets, granting exceptional salary conditions to officeholders, ratifying international and local treaties on various topics, and accepting awards from states or foreign entities). Code: Formal.
7. **Government Legislation Decision** (Decisions regarding government legislation brought to the Knesset). Code: GovLeg.
8. **Private Legislation Decision** (Decisions regarding private legislation brought to the government to formulate its stance). Code: PrivLeg.
9. **Decision to Amend or Repeal Previous Government Decisions**. Code: Amendment.
10. **Travel Approval Decision**. Code: Travel.
11. **Other Decision**. Code: Other.
"""

    # Define the user prompt
    user_prompt = f"""
    \n\nHuman:
    {system_prompt}
    {instructions}
    {key_instructions}
    {decision_type}

    Examples:
    {example_tasks}
    {example_reference}
    <text>
     {prompt}
    </text>    
    \n\nAssistant: המשימה:
    """

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ],
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "top_k": 0,
        "stop_sequences": ["\n\nHuman:"]
    }
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        assistant_response = response_body['content'][0]['text']
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    except Exception as e:
        st.error(f"An error occurred: {e}")
