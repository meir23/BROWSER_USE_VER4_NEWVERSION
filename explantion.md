BrowserContextWindowSize – מבנה נתונים למידות חלון
תיאור: BrowserContextWindowSize הוא TypedDict (מילון עם מבנה קבוע) המגדיר את גודל חלון הדפדפן. הוא כולל שני שדות: width (רוחב) ו-height (גובה), שניהם מסוג int. מבנה זה משמש כדי לקבוע את מידות חלון הדפדפן בהקשר.
דוגמה לשימוש: הגדרת גודל חלון ברוחב 1280 וגובה 1100 פיקסלים:
python
Copy
Edit
window_size = {"width": 1280, "height": 1100}
# מועבר למשל ל-BrowserContextConfig.browser_window_size
config = BrowserContextConfig(browser_window_size=window_size)
BrowserContextConfig – הגדרות עבור הקשר הדפדפן
תיאור: BrowserContextConfig היא מחלקת נתונים (@dataclass) המכילה את כל הפרמטרים להגדרת הקשר הדפדפן (Browser Context). באמצעות הגדרות אלה ניתן לשלוט בהתנהגות ההקשר – למשל האם לשמור Cookies, מה גודל החלון, אילו דומיינים מותרים לגלישה ועוד. בעת יצירת אובייקט BrowserContext חדש, ניתן להעביר מופע של מחלקה זו עם ערכים מותאמים, או להשתמש בערכי ברירת המחדל.טבלת פרמטרים מרכזיים:
פרמטר (Attribute)	סוג (Type)	ברירת מחדל (Default)	תיאור
cookies_file	str או None	None	נתיב לקובץ Cookies לצורך התמדה. אם צוין קובץ, ההקשר יטען Cookies קיימים בתחילת העבודה וישמור את העדכונים לקובץ בזמן סגירה. מאפשר לשמור מצב התחברות/גלישה בין הרצות.
disable_security	bool	True	השבתת מאפייני אבטחה בדפדפן. כאשר True, ההקשר יעקוף הגבלות כמו CSP (מדיניות אבטחת תוכן) ויתעלם משגיאות HTTPS לא מאומתות. שימושי להרצת סקריפטים באתרים מוגנים, אך פחות מאובטח.
minimum_wait_page_load_time	float	0.25	זמן המתנה מינימלי (בשניות) לאחר טעינת עמוד לפני שמערכת ה-AI אוספת את מצב העמוד. נועד להבטיח שלעמוד היה זמן להתחלה לטעון תכנים.
wait_for_network_idle_page_load_time	float	0.5	משך המתנה (בשניות) ל"רשת שקטה" לאחר טעינת עמוד. ההקשר ימתין לפרק זמן ללא בקשות רשת פעילות לפני שיאסוף את מצב העמוד, כדי לוודא שכל המשאבים נטענו.
maximum_wait_page_load_time	float	5.0	הזמן המקסימלי (בשניות) להמתין לטעינת עמוד מלאה. אם הזמן הזה חלף, המערכת תמשיך הלאה גם אם עדיין נטען משהו ברקע.
wait_between_actions	float	0.5	השהיה (בשניות) בין פעולות רציפות של הסוכן בדפדפן. מדמה קצב אנושי ומוודא שבין פעולה לפעולה הדפדפן מספיק להגיב (למשל בין הקלקה להזנת טקסט).
browser_window_size	BrowserContextWindowSize	{'width': 1280, 'height': 1100} (ברירת מחדל)	גודל חלון הדפדפן. ברירת המחדל היא 1280x1100 פיקסלים. ניתן להתאים לגודל רצוי או להשאיר לברירת מחדל.
no_viewport	Optional[bool]	None	אם הערך True, ההקשר יבוטל את הגדרת ה-viewport (כלומר ללא תצוגת מובייל מקובעת). ברירת מחדל None משמעה שימוש בערכי ברירת המחדל של Playwright (שקובע viewport לפי גודל החלון).
save_recording_path	str או None	None	נתיב תיקייה לשמירת הקלטות וידאו של ההקשר. אם צוין נתיב, ההקשר יקליט וידאו של פעולות הדפדפן וישמור בתיקייה זו. כל הקשר חדש יצור קובץ וידאו משלו.
save_downloads_path	str או None	None	נתיב תיקייה לשמירת קבצים שיורדו בדפדפן. אם צוין, הורדות מהדפדפן ישמרו אוטומטית בתיקייה זו.
trace_path	str או None	None	נתיב תיקייה לשמירת קבצי Trace (מעקב) של ההקשר. אם צוין, בעת סגירת ההקשר יישמר קובץ Trace (בפורמט ZIP) המתעד את פעילות הדפדפן, בשם ייחודי לפי מזהה ההקשר.
locale	str או None	None	מחרוזת שפה/איזור לשימוש בדפדפן (לדוגמה: "en-GB" או "he-IL"). משפיע על navigator.language, כותרת Accept-Language בבקשות, ועשוי להשפיע על פורמטים של תאריך/מספר. אם לא צוין, ייעשה שימוש בברירת המחדל של המערכת.
user_agent	str	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"	מחרוזת User-Agent מותאמת אישית לזיהוי הדפדפן מול אתרים. ברירת המחדל מזדהה כדפדפן Chrome 85 על Windows 10. ניתן לשנות כדי לדמות דפדפנים/גרסאות אחרות.
highlight_elements	bool	True	האם לסמן (Highlight) אלמנטים אינטראקטיביים בעמוד. אם True, ההקשר ידגיש אלמנטים לחיצים/קלטים על המסך (למשל באמצעות הוספת מסגרת או שכבה מעליהם) כדי לסייע בזיהוי ויזואלי.
viewport_expansion	int	500	מספר הפיקסלים מעבר לשולי חלון התצוגה (Viewport) לכל כיוון שיש לכלול באיסוף האלמנטים. למשל, 500 יכלול גם אלמנטים מעט מתחת/מעל למה שרואים כרגע. ערך 0 אומר לכלול רק אלמנטים שנמצאים ממש בתצוגה הנוכחית. ערך -1 יכלול את כל אלמנטי העמוד ללא תלות במיקומם (עלול להחזיר המון מידע).
allowed_domains	List[str] או None	None	רשימת שמות מתחם (domains) מורשים לגישה בהקשר. אם לא צוין (None), אין הגבלה על דומיינים והסוכן יכול לנווט לכל כתובת. אם מוגדר, כל ניסיון לנווט לדומיין שאינו ברשימה ייחסם ויגרום לשגיאה. למשל: ["example.com", "api.example.com"].
include_dynamic_attributes	bool	True	האם לכלול "מאפיינים דינמיים" במחוללי סלקטורים (Selectors) של אלמנטים. אם True, בעת יצירת selector לייצוג אלמנט, יילקחו בחשבון גם מאפיינים כמו data-id, data-testid וכו' שעשויים להיות דינמיים. אם רוצים selectors יציבים יותר לשימוש חוזר, ניתן להגדיר False כדי להשתמש רק במזהים סטטיים (כמו id, name, role).
_force_keep_context_alive	bool	False	שדה פנימי – אם True, אובייקט ההקשר לא יסגור את הדפדפן אוטומטית בעת ההשמדה (garbage collection). משמש בעיקר למקרי קצה או debugging כדי למנוע סגירה אוטומטית. בדרך כלל אין צורך לשנות ערך זה.
שימוש לדוגמה: יצירת הגדרות מותאמות ויצירת הקשר:
python
Copy
Edit
# יצירת הגדרות להקשר חדש
config = BrowserContextConfig(
    cookies_file="my_cookies.json",
    allowed_domains=["example.com"],
    browser_window_size={"width": 1024, "height": 768},
    highlight_elements=False
)
# יצירת אובייקט דפדפן ואז הקשר עם ההגדרות
from browser_use import Browser
browser = Browser()
context = await browser.new_context(config)
בדוגמה לעיל, ייווצר הקשר דפדפן עם ההגדרות הנתונות: טעינה/שמירה של Cookies מקובץ JSON, הגבלת גלישה לדומיין example.com, גודל חלון 1024x768 ופיצ’ר highlighting מבוטל.
BrowserSession – מידע סשן דפדפן
תיאור: BrowserSession היא מחלקת נתונים (@dataclass) פנימית המשמשת את ההקשר. היא מכילה שני שדות:
context: אובייקט Playwright BrowserContext – זהו אובייקט הספרייה החיצונית (Playwright) שמייצג בפועל את ההקשר בדפדפן (החלונות, הטאבים, ה-cookies וכו').
cached_state: אובייקט BrowserState או None – אוגר את מצב הדפדפן האחרון שנלקח באמצעות הפונקציה get_state. כלומר, לאחר קריאה ל-get_state, השדה הזה יתעדכן לשמור את עץ האלמנטים, כותרת, URL, תמונה ועוד של המצב.
בדרך כלל, למתכנת המתחיל אין צורך לגשת ישירות ל-BrowserSession. הוא מנוהל אוטומטית ע"י BrowserContext. ניתן לקבל את ה-BrowserSession דרך המתודה get_session() של ההקשר, אם יש צורך מתקדם בכך (למשל לגשת ישירות ל-Playwright context).
BrowserContextState – סטטוס פנימי של ההקשר
תיאור: BrowserContextState היא מחלקת נתונים המספקת מצב זכרון פנימי עבור ההקשר. כרגע היא מכילה שדה מרכזי אחד:
target_id: מחרוזת או None – מזהה ה"יעד" (Target ID) של ההקשר בפרוטוקול DevTools (CDP). זה משמש במקרים שבהם מחברים הקשר לדפדפן Chrome חיצוני או שומרים הפעלות. ברוב השימושים הרגילים, שדה זה יהיה None או מנוהל אוטומטית, ולא צריך לשנות אותו ידנית.
מחלקה זו ניתנת להעברה ל-BrowserContext בעת יצירתו, אך אם לא מועבר אובייקט BrowserContextState, ההקשר ייצור אובייקט חדש בעצמו. זה בעיקר שימושי אם רוצים לשמור ולשחזר מצב בין הרצות (למשל שימוש במזהה ה-target_id כדי להתחבר לאותו דפדפן).
BrowserContext – הקשר דפדפן
תיאור: מחלקת BrowserContext מייצגת הקשר דפדפן פעיל – בדומה לפרופיל או חלון דפדפן נפרד – שבו הסוכן (Agent) יכול לתפעל דפי אינטרנט. כל אובייקט BrowserContext משויך לאובייקט Browser ראשי (שמנהל את תהליך הדפדפן עצמו), ויכול להכיל מספר טאבים/עמודים. באמצעות BrowserContext אפשר לנווט בין דפים, לבצע פעולות כמו לחיצה או הקלדה, ולאסוף מידע על תוכן העמוד עבור ה-LLM (מודל השפה).בדרך כלל לא יוצרים BrowserContext ישירות באמצעות הבנאי, אלא באמצעות קריאה למתודה Browser.new_context() על אובייקט Browser. למשל:
python
Copy
Edit
from browser_use import Browser
browser = Browser()
context = await browser.new_context()  # יצירת הקשר חדש
הדוגמא לעיל תפעיל את דפדפן Playwright ברקע, תיצור הקשר דפדפן חדש ותיתן לכם אובייקט BrowserContext לשליטה. אפשר להשתמש באובייקט הזה כדי לבצע את הפעולות המתועדות להלן.
__init__(self, browser: Browser, config: BrowserContextConfig = BrowserContextConfig(), state: Optional[BrowserContextState] = None) – אתחול אובייקט הקשר
תיאור: זוהי פונקציית הבנאי של המחלקה, המופעלת בעת יצירת BrowserContext. היא אתחלת את ההקשר עם מזהה ייחודי, שומרת את אובייקט ה-Browser האב, את ההגדרות (config) ואת ה-state הפנימי (אם סופק, אחרת ייווצר חדש). הבנאי אינו פותח מיד דפדפן או טאב – זה קורה באופן דינמי כשתנסו לגשת לעמוד או לעשות פעולה (ראו get_session).
פרמטרים:
browser (Browser) – אובייקט הדפדפן הראשי שמנהל את התהליך (בד"כ מתקבל מתוך Browser.new_context). ההקשר יקושר לדפדפן הזה.
config (BrowserContextConfig) – אובייקט הגדרות עבור ההקשר. אם לא סופק, ייווצר אחד עם ברירות המחדל.
state (BrowserContextState או None) – אובייקט מצב פנימי לשימוש בהקשר. ברירת מחדל None יוצר state חדש. פרמטר זה שימושי רק אם רוצים להמשיך מצב קודם (מתקדם). מה עושה הפונקציה: מגדירה מזהה ייחודי (UUID) עבור ההקשר, טוענת את ההגדרות ומציבה את הפניות ל-Browser ול-State. כמו כן, היא מאתחלת משתנים פנימיים (כגון session) לערך התחלתי None – הם יוגדרו מאוחר יותר כשתתחיל פעילות הדפדפן.
הערה: לרוב, כמפתח לא תקרא ל-__init__ ישירות; במקום זאת תשתמש במנגנון שסופק (כמו browser.new_context()), שמטפל בקריאה לבנאי עבורך.
async def __aenter__(self) / async def __aexit__(self, exc_type, exc_val, exc_tb) – תמיכה במנהל הקשר (async with)
תיאור: שתי המתודות הללו מאפשרות להשתמש ב-BrowserContext בתוך בלוק של async with (מנהל הקשר אסינכרוני). כלומר, ניתן לכתוב:
python
Copy
Edit
async with browser.new_context() as context:
    # שימוש בהקשר
    await context.navigate_to("http://example.com")
בכניסה (בעת aenter) ההקשר מבצע אתחול של הסשן הדפדפני, וביציאה (aexit) הוא סוגר את ההקשר אוטומטית.
__aenter__: קוראת באופן אוטומטי ל-await self._initialize_session() (ראו פירוט בהמשך) כדי להפעיל את הדפדפן ולטעון הקשר, ואז מחזירה את האובייקט (self) לשימוש בתוך הבלוק.
__aexit__: דואגת לסגירת ההקשר בסיום הבלוק באמצעות await self.close(). היא מקבלת את פרטי החריגה אם התרחשה בתוך הבלוק (exc_type, exc_val, exc_tb), אך בכל מקרה תסגור את ההקשר.
שימוש לדוגמה:
python
Copy
Edit
from browser_use import Browser
browser = Browser()
async with browser.new_context() as context:
    await context.navigate_to("https://google.com")
    html = await context.get_page_html()
# בסיום הבלוק, ההקשר נסגר אוטומטית
בדוגמה, נכנסים לבלוק async with. בתחילתו, aenter יוודא שהדפדפן הותחל. בתוך הבלוק משתמשים בהקשר כרגיל. עם יציאה מהבלוק, תקרא aexit שסוגרת את ההקשר (גם אם ארעה שגיאה בתוך הבלוק).
async def close(self) – סגירת ההקשר
תיאור: מתודה זו סוגרת את ההקשר הנוכחי ואת כל המשאבים המשויכים אליו. היא תסגור את חלון הדפדפן/טאבים שנפתחו בהקשר, תשמור Cookies (אם הוגדר קובץ) ותבצע ניקוי מאזינים וחיבורים.
מה היא עושה:
רושמת ביומן (log) שההקשר נסגר לצורכי debugging.
אם עדיין לא נוצר סשן (self.session is None), אין צורך בסגירה ומחזירה מיד (אולי ההקשר לא נפתח כלל).
אם נרשם מאזין לאירועי עמוד (listener) עבור דפים חדשים, הוא יוסר כדי למנוע זליגת זיכרון.
שומרת Cookies לקובץ אם מוגדר (באמצעות save_cookies(), ראה בהמשך).
מפסיקה איסוף Trace אם הופעל (כשtrace_path בהגדרות).
סוגרת את ה-Playwright BrowserContext הפנימי (אלא אם הוגדר _force_keep_context_alive למנוע זאת).
מנקה את כל המצב הפנימי (מאפס הפניות ל-session, מאזינים וכו').
פרמטרים: אין (פרט ל-self).
ערך חזרה: None. פעולה זו אסינכרונית ויש לקרוא לה עם await.
הערות: אחרי קריאה ל-close, אובייקט ההקשר לא שמיש עוד לפעולות (כל ניסיון שימוש יגרום לשגיאה). בדרך כלל לא צריך לקרוא ל-close ידנית אם משתמשים ב-async with, אבל אם יוצרים הקשר ולא משתמשים במנהל הקשר – חשוב לזכור לסגור אותו בסיום כדי לשחרר משאבים.
דוגמה:
python
Copy
Edit
context = await browser.new_context()
# ... פעולות ...
await context.close()  # סוגר את ההקשר והדפדפן המשני
def __del__(self) – מתודת השמדה (Destructor)
תיאור: זוהי מתודה מיוחדת שפייתון קוראת כאשר אובייקט BrowserContext נאסף ע"י ה-Garbage Collector (כלומר, כבר אין אליו הפניות). היא נועדה להתריע אם ההקשר לא נסגר כראוי.
מה היא עושה: בודקת אם ההקשר לא נסגר (self.session עדיין קיים) וכן שלא ביקשו בכוונה להשאירו חי (_force_keep_context_alive False). במידה וכן – היא כותבת ליומן אזהרה שההקשר לא נסגר כראוי לפני שהושמד. היא גם תנסה לסגור את הקשר בצורה סינכרונית דרך Playwright (פעולת ניקיון אחרונה).
חשוב לדעת: מתודה זו לא מיועדת לקריאה ישירה. היא פועלת אוטומטית כאשר האובייקט נהרס. כדי למנוע אזהרות ב-del, ודאו תמיד שסגרתם הקשר באמצעות close או באמצעות async with כפי שהוסבר.
async def _initialize_session(self) – אתחול סשן הדפדפן (פרטי)
תיאור: מתודה פנימית (מוסתרת, מתחילה בקו תחתון) האחראית על הפעלת הדפדפן והקשר ה-Playwright בפועל, בפעם הראשונה שעושים שימוש בהקשר.
מה היא עושה:
אם כבר קיים סשן (כבר הופעלה בעבר), היא לא תעשה כלום. אחרת, היא תבנה אובייקט BrowserSession חדש:
היא יוצרת BrowserContext של Playwright באמצעות קריאה לפונקציה _create_context. פונקציה זו מטפלת בכל ההגדרות: יצירת חלון חדש עם המאפיינים מה-config (גודל חלון, user agent, locale וכו'), טעינת Cookies מקובץ אם יש, והפעלת סקריפטים נגד איתור אוטומציה (אנטי-דטקשן).
לאחר שיש Context של Playwright, היא רושמת מאזין לאירוע פתיחת דף חדש באמצעות _add_new_page_listener (כך שאם נפתח Tab חדש, ההקשר ידע על כך, ראה להלן).
יוצרת עמוד דפדפן ראשון (עמוד ריק התחלתי) באמצעות await context.new_page(). פעולה זו מבטיחה שיש לפחות טאב אחד לפתיחה.
שומרת את ה-BrowserSession שנוצר ב-self.session.
כמו כן, אם הוגדר דומיין או דומיינים מורשים (allowed_domains בהגדרות), תוודא שכל ניווט ייבדק מיידית ע"י _check_and_handle_navigation (שגורמת לשגיאה אם הדומיין לא ברשימה).
חשיבות: מתודה זו נקראת אוטומטית בפעם הראשונה כשמבקשים את ה-session (למשל דרך get_session או בכניסה ל-async with). אין צורך לקרוא לה ישירות, אלא אם כן אתם מבצעים הליך אתחול מותאם. היא דואגת שכל התנאים (Cookies, anti-detection, הקלטות וכו') יופעלו לפני שימוש בהקשר.
ערך חזרה: None (מבצעת אתחול, לא מחזירה אובייקט ישירות מלבד עדכון self.session).
def _add_new_page_listener(self, context: PlaywrightBrowserContext) – רישום מאזין לדפים חדשים (פרטי)
תיאור: מתודה פנימית שרושמת callback כך שכל פעם שנפתח Tab/עמוד חדש בתוך ההקשר של Playwright, ההקשר שלנו יטפל בו.
מה היא עושה: מקבלת את אובייקט ה-Playwright BrowserContext (שנוצר ב-_create_context), ומשתמשת בו לרישום listener: בכל פעם שאירוע context.on("page") מתרחש (כלומר עמוד חדש נפתח), היא תפעיל פונקציה פנימית on_page.
on_page(page: Page) (פונקציה פנימית מוגדרת בתוך _add_new_page_listener) תבצע:
בדיקה אם מוגדר חיבור לפרוטוקול CDP (Chrome DevTools Protocol) דרך הדפדפן (browser.config.cdp_url). אם כן, היא תעדכן את self.state.target_id לזהות המתאימה של העמוד החדש. (זה לצורך שמירה על זיהוי הטאב החדש בחיבור ל-Chrome חיצוני).
אין החזרה, אבל עצם הרישום מאפשר לנהל רשימת טאבים ב-Playwright (ניתן לגשת דרך session.context.pages).
מדוע זה חשוב: אם הסוכן יוצר לשונית חדשה (למשל על ידי open_tab או קליק שפותח חלון), ההקשר צריך לדעת על כך כדי שהפונקציות כמו get_current_page יעבדו גם עבור הטאב החדש. המאזין דואג לכך.
הערה: זו פונקציה פנימית ואין להשתמש בה ישירות. היא נקראת מתוך _initialize_session.
async def get_session(self) -> BrowserSession – קבלת סשן ההקשר (Lazy Initialization)
תיאור: מתודה זו מחזירה את אובייקט ה-BrowserSession של ההקשר, המאפשר גישה ל-WebBrowserContext של Playwright. קריאה לפונקציה זו תאתחל את הסשן אם הוא עוד לא קיים (ע"י קריאה ל-_initialize_session).
מה היא עושה:
אם זו הפעם הראשונה שקוראים לה (כלומר self.session הוא None), היא תקרא ל-await self._initialize_session() כדי להפעיל את הדפדפן, ליצור הקשר ועמוד התחלתי, וכן לרשום מאזינים וכו'.
לאחר מכן (או אם כבר אותחל בעבר), היא תחזיר את self.session שכעת מכיל את ה-Playwright context ואת המצב המטמון האחרון.
פרמטרים: אין (self בלבד).
החזרה: BrowserSession – אובייקט המכיל את ה-context הפנימי של Playwright (session.context) ואת ה-state האחרון (session.cached_state). לאחר קריאה ראשונה, תוכלו לקרוא שוב ולקבל את אותו אובייקט (לא מאתחל כל פעם מחדש).
דגשים: לרוב אין צורך לקרוא לפונקציה זו ישירות – היא משמשת פנימית על ידי פונקציות אחרות. אבל אם כן צריך גישה ישירה ל-Playwright context, זו הדרך.
דוגמה:
python
Copy
Edit
session = await context.get_session()
playwright_context = session.context  # אובייקט Playwright BrowserContext
print("Open pages:", len(playwright_context.pages))
בדוגמה, מקבלים את הסשן ולאחר מכן את אובייקט ה-Playwright BrowserContext, וניתן לדוגמה להדפיס כמה טאבים פתוחים יש.
async def get_current_page(self) -> Page – קבלת העמוד הנוכחי
תיאור: פונקציה זו מחזירה את אובייקט העמוד הנוכחי (טאב) שבו ההקשר פעיל. אם יש מספר טאבים פתוחים, "העמוד הנוכחי" הוא זה שבו הסוכן מתמקד כרגע. ברירת מחדל, זה יהיה העמוד האחרון שנפתח או זה ששביצעתם בו פעולת ניווט לאחרונה.
מה היא עושה:
קוראת תחילה ל-session = await self.get_session(), כדי להבטיח שיש סשן פעיל ולטעון אותו אם צריך.
לאחר מכן קוראת ל-await self._get_current_page(session) כדי לבחור את עמוד ה-Page המתאים ולהחזירו.
החזרה: אובייקט Page (של Playwright) המייצג את העמוד. עם אובייקט זה אפשר לבצע פעולות מתקדמות של Playwright, אך בדרך כלל לא נדרש באופן ישיר מאחר ו-BrowserContext מספק מתודות גבוהות יותר (navigate, execute_javascript וכו').
הערה: בפועל, _get_current_page (פונקציה פרטית) היא שקובעת איזה עמוד להחזיר: אם רק טאב אחד פתוח הוא יוחזר; אם יש כמה, ייתכן שהיא משתמשת ב-self.state.target_id כדי לזהות את הטאב הפעיל או ברירת מחדל שתחזיר את הטאב הראשון/האחרון. למתכנת המתחיל, מספיק לדעת שזו הדרך לקבל את הטאב הנוכחי לעבודה.
דוגמה לשימוש:
python
Copy
Edit
page = await context.get_current_page()
print(await page.title())  # הדפסת כותרת העמוד הנוכחי
בדוגמה, מקבלים את העמוד הנוכחי ומשתמשים ב-Playwright API (page.title()) כדי להדפיס את כותרתו.
async def _create_context(self, browser: PlaywrightBrowser) – יצירת הקשר דפדפן פנימי (פרטי)
תיאור: פונקציה פרטית זו מטפלת ביצירה בפועל של BrowserContext חדש של Playwright בהתאם להגדרות שסופקו. היא מיישמת גם אמצעי אנטי-גילוי אוטומציה (anti-detection) וטעינת Cookies אם יש.
מה היא עושה:
בודקת אם מוגדר חיבור לדפדפן חיצוני (למשל Chrome via CDP) דרך browser.config.cdp_url או browser.config.chrome_instance_path. אם כן ויש כבר הקשר פתוח, היא משתמשת בו במקום ליצור חדש (מניחה שרוצים להתחבר לדפדפן קיים).
אחרת, היא יוצרת הקשר חדש באמצעות קריאה ל-browser.new_context(...) של Playwright, עם הפרמטרים מה-BrowserContextConfig:
viewport: מוגדר לפי browser_window_size אלא אם כן no_viewport=True.
user_agent: מוגדר לפי הערך ב-config.
java_script_enabled: תמיד True (מאפשר JavaScript).
bypass_csp ו-ignore_https_errors: מוגדרים לפי disable_security (אם True, יעביר True כדי לעקוף CSP ולהתעלם מ-HTTPS שגוי).
record_video_dir ו-record_video_size: אם save_recording_path הוגדר, מפעיל הקלטת וידאו לתיקייה זו עם גודל חלון כנתון.
locale: אם הוגדר, מועבר כדי להגדיר שפת דפדפן.
אם trace_path הוגדר, מפעיל tracing באמצעות context.tracing.start(...) כדי להתחיל לאסוף נתוני trace (צילומי מסך, snapshot, קוד מקורות).
טעינת Cookies: אם בהגדרות cookies_file מצביע על קובץ קיים, היא פותחת את הקובץ, טוענת את רשימת העוגיות (בפורמט JSON) ומוסיפה אותן להקשר באמצעות context.add_cookies(cookies). כמו כן רושמת בלוג את מספר העוגיות שנטענו. פעולה זו מאפשרת המשכיות של session login וכדומה.
אמצעי Anti-detection: מייד לאחר יצירת ההקשר, הפונקציה מזריקה סקריפט (context.add_init_script(...)) לכל עמוד שיפתח בהקשר, שמגדיר מספר משתני JavaScript כדי שהאתר לא יזהה שמדובר בדפדפן אוטומטי. למשל:
הגדיר את navigator.webdriver ל-undefined (במקום true) – סימן שדפדפן לא אוטומטי.
קובע navigator.languages לערך סטנדרטי (כמו ['en-US']).
מגדיר navigator.plugins למערך מזויף.
מוסיף אובייקט window.chrome ריק, כדי להיראות כמו Chrome אמיתי.
משנה התנהגות של permissions.query כדי שתמיד יחזיר הרשאה להודעות (notifications).
מאפשר Shadow DOM גלוי (patch ל-attachShadow) – כל אלה טריקים ידועים לעקיפת בדיקות Selenium/Playwright.
לאחר ההגדרות הללו, היא מחזירה את אובייקט ה-Playwright context.
החזרה: PlaywrightBrowserContext – אובייקט ההקשר שנוצר בספריית Playwright. אובייקט זה נשמר מאוחר יותר בתוך BrowserSession.context.
הערה: פונקציה זו פנימית לחלוטין. היא נקראת מתוך _initialize_session כדי לבנות את ההקשר. כמתכנת, לא תקרא לה ישירות אלא תסמוך על המערכת שתיצור את ההקשר לפי ההגדרות.
async def _wait_for_stable_network(self) – המתנה לרשת יציבה (פרטי)
תיאור: פונקציה פנימית העוזרת להמתין עד שפעילות הרשת בעמוד נרגעה (idle), על מנת לדעת שהעמוד סיים לטעון תוכן דינמי. זה משמש אחרי ניווטים או רענון כדי לוודא שלא מפספסים תוכן נטען.
מה היא עושה:
מקבלת את העמוד הנוכחי (page = await self.get_current_page()).
מגדירה משתנה אוסף pending_requests לשמירת בקשות פעילות, ומחתימה את זמן הפעילות האחרון.
מגדירה קבוצות של סוגי משאבים ותוכן שרלוונטיים לטעינה "אמיתית" (לדוגמה: מסמכים, תמונות, CSS, JS, פונט וכו' – מסונן מרכיבי tracking, analytics, וכד').
רושמת שני מאזינים מקומיים עבור העמוד:
on_request(request): כאשר מתחילה בקשת רשת, אם סוג המשאב שלה ברשימת הרלוונטיים, היא תוסיף אותה ל-pending_requests ותעדכן את זמן הפעילות האחרון.
on_response(response): כאשר תגובה מגיעה, היא תוציא את הבקשה המתאימה מ-pending_requests (כלומר בקשה הסתיימה). אם סוג התוכן של התגובה היה רלוונטי (HTML, CSS, JS וכו'), גם תעדכן זמן פעילות.
לאחר רישום המאזינים, מתחיל לולאה שבודקת: כל עוד יש בקשות ממתינות (pending_requests לא ריק) או שעדיין בתוך חלון הזמן הרצוי – לחכות פרק זמן קטן (כמה עשרות מילישניות). משתמשים בזמן הפעילות האחרון כדי לזהות מתי עברו X שניות מאז הבקשה האחרונה.
הלולאה רצה עד ש: או שכל הבקשות הסתיימו ועבר זמן "רשת שקטה" (למשל משך wait_for_network_idle_page_load_time בהגדרות) מאז התגובה האחרונה, או שחרגנו מ-maximum_wait_page_load_time.
בסיום, מבטלת את רישום המאזינים.
שימוש פנימי: _wait_for_stable_network נקראת בתוך תהליך טעינת עמוד (למשל בתוך navigate_to או refresh_page ייתכן ומוודאים רשת יציבה). זה לא מיועד לקריאה ישירה בדרך כלל.
הערה: זמן ההמתנה מוגדר ע"י התצורה (ראו לעיל wait_for_network_idle_page_load_time ו-maximum_wait_page_load_time). אם יש אתרים שנטענים המון זמן (כמו סטרימינג) או עושים polling, הפונקציה תפסיק להמתין אחרי זמן מקסימלי.
הרשומי אירועי רשת פנימיים on_request ו-on_response (פונקציות פנימיות)
כפי שתואר לעיל, פונקציות אלה מוגדרות בתוך _wait_for_stable_network ומשמשות כ-Callback לאירועי בקשה/תגובה בעמוד. הן לא חשופות לשימוש חיצוני, אך מוסברות כדי להבין את ההקשר:
on_request(request): בעת יציאת בקשה, בודקת את request.resource_type (סוג המשאב, למשל "document" או "image") ואם הוא ברשימת המעניינים (לדוגמה מתעלמים מ"fetch" ל-analytics), היא מוסיפה את ה-id של הבקשה לסט pending_requests. כך עוקבים שיש בקשה שטרם הסתיימה.
on_response(response): בעת קבלת תגובה, מוצאת את ה-request המשויך (דרך response.request). אם סוג התוכן (response.headers.get("content-type")) מצביע שהוא מסוג המשאבים המעניינים (HTML/CSS/JS וכו'), מעדכנת את משתנה הזמן האחרון. בכל מקרה, מסירה את ה-id של הבקשה מ-pending_requests (סימן שהבקשה הסתיימה).
async def _wait_for_page_and_frames_load(self, timeout_overwrite: float | None = None) – המתנה לטעינת עמוד ו-iFrames (פרטי)
תיאור: פונקציה פנימית נוספת שמטרתה לוודא שכל ה-frames (מסגרות, iframe) בעמוד נטענו. היא לרוב נקראת אחרי פעולת ניווט או שינוי עמוד כדי לוודא שגם אם יש תוכן בתוך iframe פנימי, ממתינים לו.
מה היא עושה:
שולפת את העמוד הנוכחי (page = await self.get_current_page()).
קוראת await page.wait_for_load_state() של Playwright, אשר כברירת מחדל ממתין ל-load הראשוני.
בנוסף, עבור כל frame בתוך העמוד (כולל העמוד הראשי), היא ממתינה באופן מפורש שסטטוס הטעינה של frame זה יהיה "loaded". ייתכן שזה נעשה על ידי מעבר על page.frames וקריאה ל-frame.wait_for_load_state("load") על כל אחד.
אם timeout_overwrite סופק, ייתכן והיא משתמשת בו להגביל את סך זמן ההמתנה (במקום ברירת המחדל של Playwright).
הערה: שוב, זוהי מתודה פנימית. השילוב של _wait_for_stable_network ו-_wait_for_page_and_frames_load נותן למערכת יכולת להמתין באמת שכל חלקי העמוד עלו לפני שממשיכים. במקרים רבים Playwright מטפל בזה אוטומטית, אך זו שכבת בטחון.
def _is_url_allowed(self, url: str) -> bool – בדיקת URL מול רשימת היתרים (פרטי)
תיאור: פונקציה זו בודקת האם כתובת URL מסוימת מותרת לניווט בהתאם ל-allowed_domains שהוגדרו בהגדרות ההקשר.
פרמטרים:
url (str) – כתובת ה-URL המלאה לבדיקה (לדוגמה: "http://example.com/path").
החזרה: bool – אמת אם ה-URL מותר, שקר אם לא.
איך זה עובד:
אם allowed_domains לא הוגדר (None או רשימה ריקה), הפונקציה תחזיר תמיד True (כל URL מותר).
אחרת, היא תנתח את הדומיין מתוך ה-URL (כנראה באמצעות urllib או פעולה דומה) ותבדוק אם הדומיין הזה (והסאב-דומיין) נמצאים ברשימה.
ייתכן שהיא בודקת התאמה חלקית, למשל "example.com" יתיר גם sub.example.com. ייתכן גם שהיא תומכת בתבניות. אבל בעיקרון, אם הדומיין של ה-URL לא נכלל ברשימה, הפונקציה תחזיר False.
שימוש פנימי: משמשת בתוך ניווטים – לפני מעבר לכתובת חדשה, קוראים לה. אם מחזירה False, תיזרק שגיאת URLNotAllowedError או BrowserError למנוע את הניווט. כך שומרים שהסוכן לא ייצא מתחומי האתרים שהוגדרו.
async def _check_and_handle_navigation(self, page: Page) -> None – בדיקה וטיפול בניווט אסור (פרטי)
תיאור: מתודה פנימית שנקראת לאחר ניווט (או פתיחת עמוד חדש) כדי לוודא שלא גלשנו לדומיין אסור. במידה וכן – מטפלת בכך (למשל עוצרת את ההקשר).
מה היא עושה:
מקבלת את העמוד (Page) שבו אנחנו נמצאים לאחר ניווט. בודקת את page.url הנוכחי.
אם _is_url_allowed(page.url) מחזיר False, היא תגרום לסגירת הגלישה לאותו עמוד: קרוב לוודאי זורקת חריגה מיוחדת כגון URLNotAllowedError עם הודעה מתאימה. ייתכן ובהקשר מסוים היא גם תסגור את העמוד או תחזור אחורה, אך בעיקר המטרה להודיע שהניווט נחסם.
אם ה-URL מותר, לא עושה דבר.
שימוש: זה קורה מאחורי הקלעים בכל ניווט. למשל, בתוך navigate_to או כמאזין לפתיחת עמוד חדש, קוראים לפונקציה זו. כך, אם במסגרת פעולות הסוכן הייתה הפנייה החוצה לאתר לא מאושר, הסוכן יקבל חריגה מיד.
הערה: עבור מפתח שמשתמש ב-BrowserContext, החריגה הזו יכולה להתקבל כחריגה אסינכרונית בזמן ניווט. למשל, await context.navigate_to("http://notallowed.com") יגרום ל-BrowserError (או URLNotAllowedError) לעלות. חשוב לטפל בזה (try/except) או לוודא שרשימת הדומיינים מוגדרת כראוי.
async def navigate_to(self, url: str) – ניווט לכתובת URL
תיאור: מתודה זו גורמת לדפדפן לנווט (לעבור) לכתובת URL נתונה בטאב הנוכחי. זה שקול להקלדת הכתובת בשורת הכתובת בדפדפן ולחיצה Enter.
פרמטרים:
url (str) – כתובת ה-URL שאליה רוצים לנווט (לדוגמה: "https://www.google.com"). רצוי לכלול את הפרוטוקול (http:// או https://). מה היא עושה:
בודקת באמצעות _is_url_allowed(url) האם הכתובת מותרת (אם לא, תיזרק BrowserError עם הודעת איסור).
משיגה את העמוד הנוכחי באמצעות page = await self.get_current_page().
קוראת await page.goto(url) כדי שהדפדפן יעבור לכתובת. פעולה זו אסינכרונית וממתינה שהטעינה תתחיל.
ממתינה שעמוד ייטען במצב הבסיסי באמצעות await page.wait_for_load_state() – המתנה שטעינת העמוד הראשונית הסתיימה (דומה לאירוע onload).
(ייתכן שלאחר מכן קריאות פנימיות כמו _check_and_handle_navigation יופעלו, אבל זה שקוף למשתמש.)
הערות:
לאחר קריאה ל-navigate_to, העמוד הנוכחי בהקשר ישתנה לעמוד החדש של ה-URL.
אם רוצים לנווט ולעקוב אחרי טעינת תוכן דינמי (כמו SPA), כדאי לאחר מכן אולי לקרוא גם get_state או להשתמש במנגנוני ההמתנה המובנים.
דוגמה:
python
Copy
Edit
await context.navigate_to("https://www.wikipedia.org/")
print(await context.get_current_page().title())  # אמור להציג "Wikipedia"
בדוגמה, הניווט לויקיפדיה מתבצע. לאחר מכן נבדקת כותרת העמוד הנוכחי כדי לאשר שהניווט הצליח.
async def refresh_page(self) – רענון העמוד הנוכחי
תיאור: טוען מחדש (Refresh / Reload) את העמוד הפעיל בהקשר, כאילו המשתמש לחץ על כפתור הרענון בדפדפן.
מה היא עושה:
מאחזרת את העמוד הנוכחי (page = await self.get_current_page()).
קוראת await page.reload(), שגורם לטעינה חוזרת של אותו URL.
ממתינה לטעינה בסיסית שתסתיים עם await page.wait_for_load_state().
פרמטרים: אין (self בלבד).
הערה: זו דרך מהירה לוודא שהעמוד מעודכן, למשל אם רוצים לוודא שכל התוכן האחרון נטען.
דוגמה:
python
Copy
Edit
await context.refresh_page()
# לאחר רענון, ניתן שוב לאסוף מידע מעודכן
state = await context.get_state()
כאן אנו מרעננים את העמוד הנוכחי ואז אוספים את מצבו המעודכן.
async def go_back(self) – ניווט אחורה בהיסטוריה
תיאור: מחזיר את הדפדפן לעמוד הקודם בהיסטוריית הגלישה (Back), בדומה ללחיצה על כפתור "אחורה".
מה היא עושה:
מקבלת את העמוד הנוכחי (page = await self.get_current_page()).
מנסה ללכת אחורה: await page.go_back(timeout=10, wait_until='domcontentloaded'). קריאה זו מחזירה לדף הקודם, עם Timeout קצר (10ms) רק כדי לנסות. אם אין היסטוריה אחורה, היא תחזיר None או תיכשל בשקט.
אם הקריאה הצליחה (כלומר הייתה היסטוריה), העמוד נטען. אם לא, ייתכן ולא קרה כלום (אין עמוד אחורה ללכת אליו).
בכל מקרה, המתודה לא תחזיר ערך משמעותי, אולי רק תרשום שגיאה ל-log אם הייתה (הקוד מתעלם מחריגות כדי להמשיך גם אם העמוד לא נטען במלואו).
הערות:
שימושי לממש התנהגות "חזור" בסוכן.
אם רוצים לוודא שהעמוד חזר נטען לגמרי, אפשר אחרי זה לקרוא ל-get_state או להמתין מעט.
דוגמה:
python
Copy
Edit
await context.navigate_to("https://example.com/page1")
await context.navigate_to("https://example.com/page2")
await context.go_back()  # חוזר ל-page1
print((await context.get_current_page()).url)  # אמור להיות .../page1
async def go_forward(self) – ניווט קדימה בהיסטוריה
תיאור: ההיפך מ-go_back – מתקדם לעמוד הבא בהיסטוריה, אם קיים, בדומה ללחיצה על "קדימה".
מה היא עושה:
מאתרת את העמוד הנוכחי (page = await self.get_current_page()).
קוראת await page.go_forward(timeout=10, wait_until='domcontentloaded') כדי להתקדם קדימה. אם אין עמוד קדימה (כי לא הלכנו קודם אחורה), כנראה לא יקרה דבר.
במידה ונוצרה חריגה (למשל אם פעולה לא אפשרית), המתודה מטפלת בה בשקט (log) כדי לא לקרוס.
דגשים:
כמו go_back, אין ערך חזרה.
יש להשתמש בפונקציה זו רק לאחר שהלכת אחורה ורוצים לחזור קדימה.
דוגמה:
python
Copy
Edit
# לאחר הדוגמה הקודמת
await context.go_forward()  # מתקדם שוב ל-page2
print((await context.get_current_page()).url)  # שוב .../page2
async def close_current_tab(self) – סגירת הטאב הנוכחי
תיאור: סוגר את לשונית הדפדפן (Tab) הנוכחית בהקשר. אם יש טאבים נוספים פתוחים, יעבור אוטומטית לטאב אחר (ראשון ברשימה) כך שההקשר יישאר פעיל. אם זו הייתה הלשונית האחרונה, סגירתה תסגור למעשה את חלון הדפדפן של ההקשר.
מה היא עושה:
שולפת את הסשן באמצעות session = await self.get_session() (כדי לגשת ל-context הפנימי ולטאבים).
מאתרת את העמוד הנוכחי דרך _get_current_page(session) (העמוד שאנו מתכננים לסגור).
קוראת await page.close() לסגור את הטאב.
לאחר הסגירה, בודקת אם נשארו עוד עמודים פתוחים ב-session.context.pages.
אם כן (יש רשימת עמודים לא ריקה), קוראת await self.switch_to_tab(0) כדי לעבור לטאב הראשון ברשימה. בכך מגדירה טאב פעיל חדש בהקשר.
אם לא (הרשימה ריקה), המשמעות שהדפדפן נסגר לגמרי, כי לא נותרו טאבים פתוחים (BrowserContext של Playwright סוגר את עצמו אם כל העמודים נסגרו). במצב זה, ההקשר שלנו יהיה בעצם סגור.
החזרה: None.
דגשים:
חשוב לדעת שאם סוגרים את הטאב האחרון, למעשה לא ניתן להמשיך להשתמש בהקשר ללא פתיחת טאב חדש. ספריית Browser-Use עשויה לטפל בזה אוטומטית (למשל get_session יכול לפתוח חדש), אבל יש להיות מודעים.
ניתן לספק לסוכן פעולה "close_tab" כדי לסגור פיזית חלון קופץ או טאב שאינו נחוץ.
דוגמה:
python
Copy
Edit
# נניח שיש שני טאבים פתוחים בהקשר
await context.close_current_tab()
# עכשיו ההקשר עבר באופן אוטומטי לטאב הנותר
print(len((await context.get_session()).context.pages))  # ידפיס 1
async def switch_to_tab(self, page_id: int) -> None – מעבר לטאב לפי אינדקס
תיאור: פונקציה זו מאפשרת לתמקד (לעבור) לטאב אחר מתוך מספר טאבים פתוחים בהקשר, לפי אינדקס או מזהה. לאחר הקריאה, "העמוד הנוכחי" של ההקשר יהיה הטאב שבחרנו.
פרמטרים:
page_id (int) – ניתן לציין את אינדקס הטאב שאליו רוצים לעבור. אינדקס 0 הוא הטאב הראשון, 1 הוא השני, וכו'. אפשר גם להשתמש באינדקסים שליליים בסגנון פייתון (למשל -1 עבור הטאב האחרון).
מה היא עושה:
משיגה את אובייקט הסשן (session = await self.get_session()).
ניגשת לרשימת הטאבים הפתוחים: pages_list = session.context.pages (זו רשימת אובייקטי Page של Playwright).
מחשבת את האינדקס המבוקש: אם page_id שלילי, היא תמיר אותו לאינדקס חיובי מהסוף (כמו שעושה list בפייתון).
בודקת שהתוצאה בתחום הרשימה. אם לא, כנראה תזרוק שגיאה (IndexError או BrowserError) שהטאב לא קיים.
אם תקין, בוחרת את העמוד המתאים מתוך הרשימה, ועדכנת את ההקשר להתמקד בו. סביר שהעדכון כולל:
הגדרת self.state.target_id בהתאם לטאב שנבחר (אם מנטרים זאת).
ייתכן ושולפת את הכותרת או ה-URL של הטאב החדש למטרות לוג.
לא מבצעת ניווט חדש, רק משנה את המיקוד.
החזרה: None (רק מבצעת את השינוי).
השפעה: אחרי switch_to_tab, קריאות לget_current_page יחזירו את הטאב שבחרנו, ופעולות ניווט או איסוף מידע יתבצעו על הטאב הזה.
דוגמה:
python
Copy
Edit
# נניח שיש שני טאבים: 0- Google, 1- Wikipedia
await context.switch_to_tab(1)  # מעבר לטאב השני (Wikipedia)
print((await context.get_current_page()).url)  # ידפיס את ה-URL של Wikipedia
await context.switch_to_tab(0)  # חזרה לטאב הראשון
async def get_page_html(self) -> str – קבלת תוכן HTML של העמוד
תיאור: מתודה זו שולפת את קוד ה-HTML המלא (source) של העמוד הנוכחי. היא שימושית אם רוצים לנתח ישירות את ה-HTML או להעבירו לעיבוד.
מה היא עושה:
מוצאת את העמוד הנוכחי (page = await self.get_current_page()).
קוראת html = await page.content() – מתודת Playwright שמחזירה את כל תוכן ה-HTML של ה<html> בעמוד (לא כולל doctype).
מחזירה את המחרוזת html.
החזרה: str – מחרוזת ה-HTML.
הערה: הטקסט המוחזר עלול להיות גדול. יש להשתמש בזה בזהירות (למשל לא להדפיס את כל ה-HTML אם הוא ענק). לעיתים עדיף להשתמש ב-get_state לקבל ייצוג מתומצת של העמוד. אבל למקרי ניתוח ספציפיים, זוהי דרך ישירה לקבל את כל הקוד.
דוגמה:
python
Copy
Edit
await context.navigate_to("https://example.com")
html = await context.get_page_html()
print(html[:200])  # הצגת 200 התווים הראשונים של ה-HTML
בדוגמה, לאחר ניווט, אנו מקבלים את קוד ה-HTML ומדפיסים תחילתו.
async def execute_javascript(self, script: str) – הרצת קוד JavaScript בעמוד
תיאור: מתודה זו מאפשרת להריץ קוד JavaScript שרירותי בתוך הקשר העמוד, ולהחזיר את תוצאתו. הדבר דומה לפתיחת כלי המפתחים של דפדפן והרצת סקריפט בקונסולה.
פרמטרים:
script (str) – מחרוזת המכילה קוד JavaScript לביצוע. שימו לב, הקוד צריך להיות הערכה (evaluation) ולא פעולה אסינכרונית מתמשכת. ניתן למשל להחזיר ערכים.
מה היא עושה:
משיגה את העמוד הנוכחי (page = await self.get_current_page()).
קוראת result = await page.evaluate(script) – מתודת Playwright המזריקה את הקוד לדף ומחזירה את הערך שהסקריפט החזיר.
מחזירה את result. התוצאה יכולה להיות טיפוס פשוט (מספר, מחרוזת, אובייקט serializable) בהתאם למה שהסקריפט עשה. אם הסקריפט לא החזיר כלום, סביר שהתוצאה תהיה None.
החזרה: ערך Python שמשקף את תוצאת הקוד.
דגשים:
יש לוודא שהסקריפט לא תלוי במשתנים חיצוניים בפייתון – הוא רץ בדפדפן. אפשר למשל לעשות return document.title; בתוך הסקריפט כדי לקבל ערך.
אם הסקריפט מבצע פעולות שאינן מחזירות ערך, אפשר עדיין להריץ אותן, פשוט יקבלו None.
דוגמה:
python
Copy
Edit
# הוספת אלמנט חדש לדף דרך JavaScript
script = "document.body.appendChild(document.createElement('div')); return document.body.children.length;"
children_count = await context.execute_javascript(script)
print(f"Children count: {children_count}")
בדוגמה, אנו מריצים סקריפט שמוסיף <div> חדש לגוף העמוד, ומחזירים את מספר הילדים תחת <body>. הפלט יודפס כמספר.
async def get_page_structure(self) -> str – קבלת מבנה עמוד לתצוגה
תיאור: פונקציה זו מחזירה מבנה טקסטואלי למטרות דיבוג של מבנה ה-DOM של העמוד, כולל iframe-ים. זוהי תצוגה מתומצתת שמציגה היררכיה של אלמנטים, מזהים, מחלקות ונתונים רלוונטיים (aria, src, וכו').
מה היא עושה:
מגדירה סקריפט JavaScript (די מורכב) שמבנה את ההיררכיה של אלמנטים בעמוד. הסקריפט, למשל, עובר על כל העץ (עד עומק מסוים, כמו 10), מדלג על תגיות לא רלוונטיות (script, style וכד'), ומדפיס כל אלמנט עם הזחה לפי רמתו. עבור כל אלמנט, מציג את שם התג, ואם יש id – מוסיף #id, ואם יש מחלקות – מציג .class1.class2. כמו כן, מוסיף רשימת מאפיינים נבחרים (role, aria-label, type, name, src וכו' – חותך src אם ארוך).
מתייחס במיוחד ל-iframe: כאשר מגיע ל<iframe>, הסקריפט מנסה לגשת למסמך הפנימי (contentDocument) ואם מצליח – כותב שורה "[IFRAME CONTENT]:" וכולל את מבנה ה-DOM הפנימי של ה-iframe (עם הזחה נוספת). אם ה-iframe חיצוני (דומיין אחר) ואין גישה, מציג הודעה על כך.
מריץ את הסקריפט באמצעות await page.evaluate(debug_script).
מקבל חזרה את המחרוזת structure – המכילה שורות טקסט של המבנה.
מחזיר את המחרוזת.
החזרה: str – טקסט בפורמט קריא לאדם המציג את מבנה העמוד.
שימוש טיפוסי: מיועד בעיקר לפיתוח ודיבוג, כדי להבין מה רואה הסוכן (למשל אילו אלמנטים לחיצים יש ובאיזה מבנה).
דוגמה (פלט לדוגמה):
נניח בעמוד יש מבנה פשוט, get_page_structure עשוי להחזיר משהו כמו:
less
Copy
Edit
html
 head
 body
   div#main.container [role="main"]
     h1.title 
     p 
       a.link [href="http://..."]
   iframe#iframe1
    [IFRAME CONTENT]:
      html
       head
       body
         p ...
הפלט ממחיש את ההיררכיה והמאפיינים החשובים.
async def get_state(self) -> BrowserState – קבלת מצב העמוד להסקת AI
תיאור: זוהי אחת הפונקציות המרכזיות של BrowserContext. היא אוספת את מצב העמוד הנוכחי בפורמט שמיש עבור סוכן AI. מצב זה (BrowserState) כולל את עץ האלמנטים האינטראקטיביים, מיפוי סלקטורים, כתובת URL, כותרת העמוד, רשימת טאבים, תמונת מסך מקודדת, ומידע גלילה. מטרתה לספק למודל השפה תמונת מצב עדכנית של מה שקורה בדפדפן.
מה היא עושה:
המתנה לטעינה מלאה: קוראת await self._wait_for_page_and_frames_load() כדי לוודא שהעמוד וכל ה-iFrames בו נטענו לגמרי.
משיגה את הסשן (session = await self.get_session()).
מעדכנת את המצב המטמון: session.cached_state = await self._update_state(). כלומר, מפעילה את _update_state (ראו פירוט מיד) כדי לאסוף את כל נתוני העמוד, ושומרת את התוצאה כמצב הנוכחי.
אם בקובץ ההגדרות הוגדר cookies_file, מפעילה באופן אסינכרוני (ברקע) משימת שמירת Cookies: asyncio.create_task(self.save_cookies()). זאת אומרת, בלי להמתין, יוזמת שמירת cookies עדכנית לקובץ, כדי להתמיד session.
מחזירה את האובייקט session.cached_state שהתקבל, שהוא מסוג BrowserState. אובייקט זה מכיל, בין היתר:
element_tree: מבנה הנתונים של עץ האלמנטים האינטראקטיביים (למשל רשימה של אלמנטים עם המאפיינים החשובים לכל אחד – טקסט, סלקטור, האם לחיץ וכו'). זה מופק על-ידי DomService.
selector_map: מיפוי בין מזהי אלמנט (אינדקסים) לסלקטורים שלהם ב-DOM, כדי שהסוכן יוכל למשל להגיד "לחץ על כפתור 5" בהתבסס על אינדקס.
url: כתובת העמוד הנוכחי.
title: כותרת העמוד הנוכחי.
tabs: מידע על הטאבים הפתוחים (רשימה שיוחזרה מ-get_tabs_info()).
screenshot: תמונת מסך של העמוד הנוכחי בפורמט Base64 (מחרוזת ארוכה).
pixels_above / pixels_below: מספר הפיקסלים שגלולים מעל ומתחת לתצוגה הנוכחית (לצרכי הבנה כמה עוד תוכן יש לגלול).
החזרה: אובייקט BrowserState המכיל את כל המידע הנ"ל.
שימוש: מתודה זו מיועדת להיקרא על ידי הסוכן בכל שלב שבו הוא רוצה להבין את העמוד לפני החלטה על פעולה. היא מרכזית מאוד בתהליך ה-loop של סוכן ה-LLM.
דוגמה:
python
Copy
Edit
state = await context.get_state()
print(state.url)        # מציג את ה-URL הנוכחי
print(state.title)      # מציג את כותרת העמוד
print(len(state.tabs))  # כמות טאבים פתוחים
print(len(state.element_tree))  # מספר אלמנטים אינטראקטיביים שנמצאו בעמוד
בדוגמה, לאחר קריאה ל-get_state, אנו משתמשים במאפיינים שונים של ה-BrowserState. למשל, URL, כותרת, מספר טאבים ואלמנטים.
async def _update_state(self, focus_element: int = -1) -> BrowserState – עדכון והחזרת מצב (פרטי)
תיאור: פונקציה פנימית זו מבצעת את העבודה בפועל של איסוף מצב העמוד ויצירת אובייקט BrowserState. ניתן לראות בה את "מנוע" ה-get_state. היא מחזירה את ה-BrowserState החדש.
פרמטרים:
focus_element (int) – ברירת מחדל -1. פרמטר זה עשוי לציין אם יש אלמנט ספציפי שבפוקוס או שיש להתמקד בו. למשל, אם פונקציה חיצונית רוצה להתמקד באלמנט מסוים בעת איסוף המידע (highlight). בערך -1 כנראה אין אלמנט ספציפי.
מה היא עושה:
משיגה את הסשן (session = await self.get_session()), שכולל את רשימת העמודים הפתוחים.
מוודאת שהעמוד הנוכחי עדיין קיים ותקין:
מנסה לקבל את העמוד הנוכחי (page = await self.get_current_page()), ואז מריצה עליו await page.evaluate('1') כבדיקת תקינות (מריצה פקודת JavaScript טריוויאלית).
אם זה נכשל (Exception) – יומן רושם שהעמוד כבר לא נגיש (אולי נסגר או קרתה שגיאה).
במקרה כזה, מנסה לתקן: שולף את רשימת כל הטאבים pages = session.context.pages. אם הרשימה לא ריקה, מאפסת את self.state.target_id ובוחרת טאב אחר להיות פעיל (page = await self._get_current_page(session)). רושמת לוג שהחליפה טאב וכנראה גם מציגה את כותרתו. אם אין בכלל דפים (רשימה ריקה), זורקת BrowserError("Browser closed: no valid pages available") – אין על מה לעבוד.
מסירה הדגשות קודמות: קוראת await self.remove_highlights(). (במידה והמנגנון סימן קודם אלמנטים, מורידים את ההדגשות כדי שהמצב החדש יהיה נקי – ראו פירוט remove_highlights בהמשך).
יוצר מופע של שירות DOM: dom_service = DomService(page). זהו אובייקט (ממחלקה DomService) שאחראי לאסוף אלמנטים לחיצים וטקסטים מהעמוד.
קורא content = await dom_service.get_clickable_elements(... ) עם מספר פרמטרים:
focus_element=focus_element (אם -1 אז אין מוקד מיוחד),
viewport_expansion=self.config.viewport_expansion (לכלול אלמנטים קצת מעל/מתחת לתצוגה כפי שהוגדר),
highlight_elements=self.config.highlight_elements (אם True, DomService יוסיף סימון/מספור על האלמנטים בעמוד).
קריאה זו מחזירה אובייקט (נניח מסוג תוכן כלשהו) המכיל element_tree ו-selector_map. אלו בעצם הנתונים המעובדים: רשימת אלמנטים אינטראקטיביים (כפתורים, קישורים, שדות קלט וכו') עם המאפיינים החשובים שלהם, ומפה ממספר לכל סלקטור CSS ייחודי שלהם.
לוקח צילום מסך: screenshot_b64 = await self.take_screenshot(). זו מתודה שתצלם את העמוד (ראה להלן take_screenshot) ותחזיר Base64.
מחשב מידע גלילה: pixels_above, pixels_below = await self.get_scroll_info(page). פונקציה זו (ראה פירוט get_scroll_info) תחזיר כמה פיקסלים נמצאים מעל אזור התצוגה הנוכחי (גלולים כבר) וכמה מתחתיו (נשאר לגלול).
כעת יוצר אובייקט BrowserState:
python
Copy
Edit
self.current_state = BrowserState(
    element_tree=content.element_tree,
    selector_map=content.selector_map,
    url=page.url,
    title=await page.title(),
    tabs=await self.get_tabs_info(),
    screenshot=screenshot_b64,
    pixels_above=pixels_above,
    pixels_below=pixels_below,
)
כלומר מזין את כל הנתונים שנאספו: עץ אלמנטים, מפת סלקטורים, URL נוכחי, כותרת נוכחית (דורש await page.title()), רשימת טאבים (דורש await self.get_tabs_info() – ראה בהמשך), תמונת מסך, וכמות גלילה מעל/מתחת.
שומר את אובייקט זה ב-self.current_state.
מחזיר את self.current_state.
במקרה של חריגה בכל התהליך, ירשום שגיאה ללוג. אם היה כבר מצב קודם (self.current_state קיים), יחזיר אותו כאחרון ידוע ולא יקרוס (זה טיפול תקלות – עדיף להחזיר מידע ישן מאשר כלום). אם לא היה מצב קודם, יזרוק את החריגה.
החזרה: BrowserState – אובייקט עם מצב העמוד כפי שתואר.
הערה: מפתח רגיל לא יקרא ל-_update_state ישירות, אלא ישתמש ב-get_state. אך הידיעה מה _update_state עושה נותנת הבנה עמוקה של מה מכיל ה-state וכיצד נאסף.
async def take_screenshot(self, full_page: bool = False) -> str – צילום מסך העמוד
תיאור: מתודה זו מצלמת את התצוגה של העמוד הנוכחי ומחזירה את התמונה בפורמט Base64 (מחרוזת). ניתן לבחור אם לצלם את כל העמוד (גלילה מלאה) או רק את האזור הנראה.
פרמטרים:
full_page (bool) – ברירת מחדל False. אם True, יתפוס צילום של העמוד כולו מלמעלה עד למטה (עשוי להיות ארוך), אם False – רק מה שרואים על המסך (viewport) כרגע.
מה היא עושה:
משיגה את העמוד הנוכחי (page = await self.get_current_page()).
מביאה את החלון לקדמה: await page.bring_to_front() – במיוחד אם יש מספר חלונות/הקשרים, מוודאת שהחלון הזה בפוקוס לצילום.
ממתינה שעמוד יהיה טעון: await page.wait_for_load_state().
לוקחת צילום מסך:
python
Copy
Edit
screenshot_bytes = await page.screenshot(full_page=full_page, animations='disabled')
(מגדירה גם animations='disabled' כדי לעצור אנימציות בזמן הצילום, לקבל תמונה יציבה). פעולה זו מחזירה bytes של תמונת PNG.
ממירה את ה-bytes לבסיס 64: screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8').
מחזירה את המחרוזת screenshot_b64.
החזרה: str – מחרוזת Base64 המייצגת את תמונת המסך (ניתן לשמור לקובץ ע"י פיענוח או להטמיע ב-HTML בתגית <img src="data:image/png;base64,...">).
דוגמה:
python
Copy
Edit
img_data = await context.take_screenshot(full_page=True)
# שמירת צילום המסך לקובץ לשם דוגמה:
with open("page.png", "wb") as f:
    f.write(base64.b64decode(img_data))
בדוגמה, צילמנו את כל העמוד ושמרנו את התמונה כקובץ "page.png".
async def remove_highlights(self) – הסרת הדגשות מהעמוד
תיאור: פונקציה זו מסירה מהעמוד הנוכחי כל סימוני Highlight שנוצרו על-ידי המערכת. למשל, אם DomService או פעולות אחרות הוסיפו מסגרות ותיוגים לאלמנטים (כדי לסמן למשתמש איזה אלמנט הוא מספר 1, 2 וכו'), הפונקציה תנקה אותם כדי לא להשאיר "לכלוך" על העמוד.
מה היא עושה:
מנסה לקבל את העמוד הנוכחי (page = await self.get_current_page()). אם אין עמוד (סגור), תהיה חריגה מטופלת.
מריצה JavaScript דרך page.evaluate(...) שמבצע:
מחיקה של האלמנט בעל ה-id playwright-highlight-container אם קיים (זה כנראה קונטיינר שהוכנס לעמוד כדי לאגד את סימוני ההדגשה).
הסרת כל attributes בשם browser-user-highlight-id מכל האלמנטים שסומנו (ייתכן וכל אלמנט שסומן קיבל attribute כזה).
הקוד עטוף ב-try/catch כדי שלא יעשה בעיות אם משהו לא קיים.
במידה וההרצה נכשלה (למשל העמוד לא זמין), הפונקציה תתפוס את החריגה, תרשום הודעת debug ללוג אבל לא תזרוק שגיאה החוצה (כי זה לא קריטי).
החזרה: None.
הערה: משתמשי קצה בדרך כלל לא יקראו לפונקציה זו ישירות, כי היא משולבת בתהליך איסוף state. אך אם למשל מדגישים אלמנטים ידנית דרך JavaScript, אפשר להשתמש בה לנקות. הפונקציה נועדה לשמור על DOM נקי לפני צילום מסך או איסוף נתונים חדש.
@classmethod def _convert_simple_xpath_to_css_selector(cls, xpath: str) -> str – המרת XPath פשוט ל-CSS Selector (פרטי, מתודת מחלקה)
תיאור: מתודה סטטית/מחלקתית פנימית, הממירה ביטוי XPath פשוט לביטוי CSS Selector מקביל. היא מטפלת רק ב-XPath "פשוט" – לרוב כזה שניתן על ידי DomService לכל אלמנט – ומנסה לתרגם אותו ל-Selector שנוכל להשתמש בו ב-JavaScript או CSS.
פרמטרים:
xpath (str) – מחרוזת XPath (כמו "/html/body/div[2]/button[1]").
החזרה: str – מחרוזת selector ב-CSS המתאים (כמו "html > body > div:nth-of-type(2) > button:nth-of-type(1)"). אם אינה מצליחה לתרגם, תחזיר מחרוזת CSS חלקית או ריקה.
איך היא פועלת:
אם ה-XPath ריק או None, מיד מחזירה מחרוזת ריקה.
מסירה מה-XPath קו נטוי מוביל אם יש (למשל הופך "/div/span" ל-"div/span").
מפצלת את ה-XPath לחלקים לפי '/', כך שכל חלק מייצג צעד בעץ (תגית ואופציונלית אינדקס).
עבור כל חלק:
אם החלק ריק (יכול לקרות אם ה-XPath מתחיל ב'//' לדוגמה) – מדלג.
אם החלק מכיל סוגריים מרובעים [...] (כלומר אינדקס או פונקציה):
מפריד את שם התג הבסיסי (base_part) מהאינדקסים. למשל "div[2]" -> base_part = "div", index_part = "[2]". או מספר אינדקסים אם יש.
עבור כל אינדקס במחרוזת index_part:
מנסה לפרש את התוכן בתוך הסוגריים. אם זה מספר (נגיד "3"), הופך אותו לסלקטור :nth-of-type(3) (אבל שימו לב: ב-XPath האינדקסים מבוססי-1, ב-CSS גם מבוססי-1, אז כנראה ישירות).
אם זה "last()", ממיר ל:last-of-type.
אם זה ביטוי position()>1 וכדומה, ממיר ל:nth-of-type(n+2) (כלומר כל פרט מהשני והלאה).
התעלמות או המשך אם אינדקס לא מתורגם.
מוסיף את ה-base_part עם התוספות של ה-nth-of-type לרשימת חלקי ה-CSS.
אם החלק לא מכיל סוגריים (אין אינדקס, כלומר בודד), מוסיף אותו כפי שהוא לרשימת חלקי ה-CSS.
מחבר את חלקי ה-CSS עם ' > ' ביניהם (כלומר child combinator בין רמות).
מחזיר את המחרוזת המלאה.
הערה: לא כל XPath כללי ניתן לתרגום ישיר ל-CSS Selector. הפונקציה הזאת מטפלת במקרים נפוצים (תגיות עם אינדקסים, last(), אולי position()). זה משמש פנימית כחלק מיצירת סלקטורים ידידותיים.
@classmethod def _enhanced_css_selector_for_element(cls, element: DOMElementNode, include_dynamic_attributes: bool = True) -> str – יצירת סלקטור CSS משופר עבור אלמנט (פרטי, מתודת מחלקה)
תיאור: מתודה מחלקתית פרטית זו בונה CSS Selector ייחודי לאלמנט נתון, תוך התחשבות בכל מיני מקרים מיוחדים ותווים מיוחדים. מטרתה ליצור Selector יציב ושמיש ככל האפשר לזיהוי האלמנט.
פרמטרים:
element (DOMElementNode) – אובייקט המייצג אלמנט ב-DOM (כפי שחוזר מ-DomService, כנראה כולל לפחות xpath וattributes).
include_dynamic_attributes (bool) – האם לכלול במבחן גם מאפיינים "דינמיים" כמו data-id וכד' (True כברירת מחדל, בהתאם לפרמטר במצב ההקשר).
מה היא עושה:
מנסה ליצור בסיס של selector מתוך ה-XPath:
css_selector = cls._convert_simple_xpath_to_css_selector(element.xpath)
כמתואר לעיל, מקבלת Selector בסיסי (למשל "div > button:nth-of-type(2)").
התייחסות למחלקות (class): אם לאלמנט יש attribute 'class' והוא לא ריק, והיא כוללת dynamic attributes:
מגדירה regex לבדיקת שמות מחלקה חוקיים ב-CSS (אות או קו תחתון בהתחלה, ואח"כ אותיות/ספרות/מקפים/_).
מפצלת את מחרוזת המחלקות לרשימה.
עבור כל שם מחלקה ברשימה:
מתעלמת ממחרוזת ריקה (אם היו רווחים כפולים וכו').
בודקת שהשם עומד בפורמט התקין (ע"פ regex, כדי שלא יכיל תווים בעייתיים לסלקטור).
אם תקין, מוסיפה ל-selector את הסימן .שםמחלקה (כלומר דורשת שהאלמנט מכיל את המחלקה הזו).
אם השם לא חוקי, מדלג (כדי לא לשבור את הסלקטור).
מאפיינים נוספים: מגדירה סט של מאפיינים "בטוחים" (SAFE_ATTRIBUTES) שהם יציבים ושימושיים לסלקטור:
כולל: id, name, type, placeholder, aria-label, aria-labelledby, aria-describedby, role, for, autocomplete, required, readonly, alt, title, src, href, target.
אם include_dynamic_attributes True, מוסיפה גם מאפיינים דינמיים נפוצים: data-id, data-qa, data-cy, data-testid.
עוברת על כל attribute של האלמנט (מתוך element.attributes המילון):
מתעלמת מ-class (כבר טופל) או מערכים לא חוקיים (שם ריק).
אם שם המאפיין לא ברשימת SAFE_ATTRIBUTES, מדלג (לא נחשב "יציב" מספיק או פשוט לא רלוונטי).
עבור שם מאפיין שנכלל:
מייצר גרסה "בטוחה" של שם המאפיין לשימוש בסלקטור – למשל מחליף : בפליטה \: (נקודתיים צריך לברוח ב-CSS).
מתייחס לערך: אם הערך ריק, אם הערך ארוך, ייתכן ולא ישתמש; אבל הקוד המלא לא מולנו. סביר ש:
אם הערך הוא מחרוזת, עוטף אותו בסימנים מתאימים.
אם זה id, אולי כבר היה מטופל ע"י ה-xpath, אבל לא בטוח.
מוסיף לסלקטור קטע כמו [name="value"] או [role="button"] וכד'.
ממשיך כך עבור כל attribute מתאים, כך שלבסוף נקבל CSS Selector שמציין גם את התג (מה-XPath), גם מחלקות, וגם אולי מאפיינים ייחודיים שמבדילים את האלמנט.
מחזיר את המחרוזת הסופית של ה-Selector.
החזרה: str – סלקטור CSS ייחודי לאלמנט.
שימוש: פנימי בלבד, ככל הנראה בשלב יצירת ה-selector_map בתוך DomService/BrowserContextState. למפתח קצה זה מידע, כי ייתכן וה-selector_map שתראו ב-BrowserState נוצר באמצעות פונקציה זו – כך שהוא יהיה CSS Selector שניתן למשל להזין ל-execute_javascript אם רוצים לאתר אלמנט.
async def get_scroll_info(self, page: Page) -> tuple[int, int] – מידע גלילה אנכי
תיאור: פונקציה זו מחשבת כמה תוכן בעמוד נמצא מעל ומתחת לנקודת הגלילה הנוכחית (כלומר, כמה כבר גללנו וכמה עוד ניתן לגלול). זה עוזר להחליט אם צריך לגלול מטה כדי לחשוף עוד תוכן.
פרמטרים:
page (Page) – אובייקט עמוד של Playwright שאת נתוני הגלילה שלו בודקים. בד"כ זה העמוד הנוכחי.
מה היא עושה:
מבצעת הערכת JavaScript בעמוד כדי לקבל שלושה נתונים:
המיקום הנוכחי של הגלילה (window.scrollY – כמה פיקסלים גוללו מלמעלה).
גובה החלון הנראה (window.innerHeight – גובה ה-viewport).
הגובה הכולל של תוכן הדף (document.body.scrollHeight – כמה פיקסלים כל התוכן בגוף העמוד תופס).
מחשבת:
pixels_above = scrollY (כמה פיקסלים מוסתרים מעל בגלל הגלילה).
pixels_below = scrollHeight - (scrollY + innerHeight) (כמה פיקסלים של תוכן עוד נמצאים מתחתית החלון, כלומר כמה עוד אפשר לגלול למטה). אם הערך שלילי, מניחים 0.
מחזירה את הזוג (pixels_above, pixels_below).
החזרה: Tuple[int, int] – מספר הפיקסלים מעל, מספר הפיקסלים מתחת.
דוגמה: אם למשל העמוד בגובה 3000px, החלון 800px, וגוללנו 400px מטה:
pixels_above = 400
pixels_below = 3000 - (400 + 800) = 1800
הפונקציה תחזיר (400, 1800).
שימוש: מנגנון הגלילה האוטומטי של הסוכן יכול להשתמש בזה כדי לדעת מתי הוא בקצה העמוד. גם ה-BrowserState מחזיר ערכים אלו כחלק מהמצב.
async def get_tabs_info(self) -> List[TabInfo] – מידע על טאבים פתוחים
תיאור: פונקציה זו אוספת ומחזירה רשימת מידע על כל הטאבים (חלוניות) הפתוחים בהקשר הנוכחי. כך הסוכן יכול לדעת אילו דפים פתוחים במקביל.
מה היא עושה:
משיגה את ה-session (session = await self.get_session()).
שולפת את רשימת העמודים הפתוחים: pages = session.context.pages (רשימת Page). סדר הרשימה הוא ככל הנראה סדר הפתיחה (הראשון ברשימה הוא הראשון שנפתח, האחרון הוא האחרון).
עבור כל עמוד ב-pages, אוספת מידע כגון:
כותרת העמוד (await page.title()),
ה-URL של העמוד (page.url),
אולי גם אינדקס הטאב (המיקום ברשימה).
אפשרות: מציבה דגל מי מהטאבים הוא הנוכחי/פעיל. ייתכן שמשתמשים ב-self.state.target_id או משווים את page הנוכחי (מ-get_current_page) לזה שביד.
יוצרת אובייקטי TabInfo (אם מחלקה כזו מוגדרת) עבור כל טאב, המכילים שדות כמו: index, title, url, וייתכן active (במידה וסמנים את הפעיל).
מחזירה את רשימת ה-TabInfo הללו.
החזרה: List[TabInfo] – רשימה של אובייקטים (או מילונים) עם מידע על כל טאב. לדוגמה:
python
Copy
Edit
[
  TabInfo(index=0, title="Google", url="https://google.com", active=True),
  TabInfo(index=1, title="Example Domain", url="https://example.com", active=False)
]
(מבנה מדויק עשוי להשתנות, אך הרעיון הוא רשימת טאבים עם פרטי זיהוי).
שימוש: מידע זה נכלל ב-BrowserState.tabs. ניתן להשתמש בו כדי להחליט לעבור לטאב מסוים. למשתמש הקצה, אפשר למשל להדפיס את רשימת הכותרות של טאבים פתוחים כדי להבין מה פתוח:
python
Copy
Edit
tabs = await context.get_tabs_info()
for tab in tabs:
    print(f"Tab {tab.index}: {tab.title} ({tab.url}){' [ACTIVE]' if tab.active else ''}")
async def save_cookies(self) – שמירת Cookies לקובץ
תיאור: מתודה זו שומרת את כל ה-Cookies הנוכחיים של ההקשר לקובץ שהוגדר ב-BrowserContextConfig.cookies_file. מטרתה לתמוך בהתמדה של מצב התחברות/ביקור בין הרצות, כך שהפעם הבאה שתיווצר הקשר עם אותו cookies_file, הוא יטען את העוגיות הללו.
מה היא עושה:
בודקת אם בהגדרות קיים נתיב בקובץ self.config.cookies_file. אם לא הוגדר, הפונקציה לא תבצע דבר (אין לאן לשמור).
משיגה את ה-session וההקשר הפנימי (session = await self.get_session()).
שולפת את רשימת ה-Cookies הנוכחיים מההקשר: cookies = await session.context.cookies(). מתודת Playwright זו מחזירה רשימה של מילוני Cookie, כאשר כל מילון מכיל שדות כמו name, value, domain, path, expiry וכו'.
פותחת את הקובץ המצוין בנתיב לכתיבה (בפורמט טקסט) וכותבת לתוכו את רשימת ה-Cookies בפורמט JSON: json.dump(cookies, file, indent=2) או דומה.
סוגרת את הקובץ.
ייתכן ורושמת בלוג הודעה על שמירת כמות ה-Cookies.
החזרה: None.
הערה: פעולה זו נקראת אוטומטית בשני מקרים:
בתוך close(), לפני סגירה – מוודאת שכל cookies נשמרו.
בתוך get_state(), אחרי עדכון מצב – מזניקה save ברקע (לא מחכה) כדי לעדכן את הקובץ במהלך הריצה.
כך או כך, אין צורך לקרוא לה ישירות בדרך כלל. רק ודאו שcookies_file הוגדר אם רוצים התמדה, והשאר יקרה אוטומטית.
דוגמה:
python
Copy
Edit
context = await browser.new_context(BrowserContextConfig(cookies_file="cookies.json"))
await context.navigate_to("https://example.com/login")
# ... ביצוע התחברות, עכשיו נניח יש Cookies ...
await context.save_cookies()  # שומר ידנית (לרוב לא צריך, יישמר בסגירה אוטומטית)
לאחר סגירת ההקשר, בקובץ "cookies.json" תהיה רשימה של cookies. בהרצה הבאה אם שוב יוצרים הקשר עם אותו cookies_file, ה-_create_context כבר יטען אותם, וכך תהיו עדיין מחוברים.
סיכום: מחלקת BrowserContext וכל הפונקציות שתוארו לעיל מספקות ממשק עשיר לשליטה בדפדפן דרך סוכן AI או קוד פייתון אסינכרוני. למתכנת המתחיל, עיקר הפונקציות שישתמש בהן ישירות הן:
navigate_to(url) – כדי לעבור לעמוד מסוים.
get_page_html() / execute_javascript() – אם צריך למשוך מידע גולמי מהעמוד.
get_state() – כדי לקבל תמונת מצב מלאה של העמוד עבור עיבוד מתקדם (למשל הזנה למודל שפה).
פעולות ניווט: refresh_page(), go_back(), go_forward(), open_tab (דרך navigate_to עם URL חדש או פונקציה ייעודית אם תהיה), close_current_tab(), switch_to_tab() – לניהול מולטי-טאב.
take_screenshot() – לצילום מסך אם רוצים.
רובן ככולן אסינכרוניות, לכן יש לזכור לקרוא להן עם await. ההסברים שלעיל נועדו לתת גם את התמונה הפנימית, אך בשימוש בסיסי תוכלו להסתפק בכמה פונקציות מפתח. שילוב שלהן בקוד צריך להיעשות בתוך פונקציה אסינכרונית (או Jupyter environment תומך) ולהשתמש בתחביר async/await.