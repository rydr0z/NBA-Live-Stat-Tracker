import streamlit as st

from webapp.webapp import run_webapp


def main():
    if True:
        st.image("NBA Stat Logo.png")
        st.title("NBA All Star Game")
        st.write("Check back when regular season resumes")
    else:
        run_webapp()
    print("Starting NBA Stats WebApp")


if __name__ == "__main__":
    main()
