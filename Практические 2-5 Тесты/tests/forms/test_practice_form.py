from pathlib import Path
from faker import Faker
from utils.data_loader import load_json
from pages.forms.practice_form_page import PracticeFormPage

fake = Faker()

def test_practice_form_happy_path(page):
    cfg = load_json("data/practice_form.json")

    picture = Path("artifacts/uploads/picture.png")
    picture.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal stub, DemoQA only checks filename

    first = fake.first_name()
    last = fake.last_name()
    email = fake.email()
    mobile = "9000000000"

    pf = PracticeFormPage(page).open_page()
    pf.fill_main(first, last, email, mobile)
    pf.select_gender(cfg["gender"])
    pf.set_birth_date(cfg["birth_date"])
    for s in cfg["subjects"]:
        pf.add_subject(s)
    for h in cfg["hobbies"]:
        pf.select_hobby(h)
    pf.upload_picture(str(picture))
    pf.fill_address("Pavlodar")
    pf.select_state_city(cfg["state"], cfg["city"])
    pf.submit()

    pf.assert_modal_contains({
        "Student Name": f"{first} {last}",
        "Student Email": email,
        "Gender": cfg["gender"],
        "Mobile": mobile,
        "Subjects": cfg["subjects"][0],
        "Hobbies": cfg["hobbies"][0],
        "Picture": picture.name,
        "Address": "Pavlodar",
        "State and City": f"{cfg['state']} {cfg['city']}",
    })

def test_practice_form_required_validation(page):
    pf = PracticeFormPage(page).open_page()
    pf.submit()
    pf.assert_not_submitted()
    pf.assert_required_invalid()
