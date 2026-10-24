import streamlit as st


def main():
    st.title("📚 Sources and Limitations")
    st.markdown(
        """
        The dashboard relies sur a single dataset de l'Assurance Maladie (Cnam),
        published on data.gouv.fr, concerning patient numbers de patients par pathologie, sexe,
        classe d'age et territoire.
        """
    )

    st.subheader("Methods used")
    st.markdown(
        """
        - Raw prevalence : sum of patients / sum of population sur les cases concernees.
        - Standardized prevalence : average of prevalences par case age-sexe weighted by une reference population fixe.
        - Comparative Index : observed patients / expected patients, avec exclusion coherente des cases NS ou inexploitables.
        - Total lines et NS values are excluded afin d'avoid double counting et les biais.
        """
    )

    st.subheader("Limitations")
    st.markdown(
        """
        - Prevalence measures patients treated, et not only the disease elle-meme.
        - Territorial analysis does not allow conclusions about individuals.
        - Data does not replace une finer study of healthcare access ou des social determinants.
        - Les valeurs manquantes (NS) sont treated as missing and not as zero.
        """
    )

    st.subheader("Source")
    st.write("https://www.data.gouv.fr/datasets/pathologies-effectif-de-patients-par-pathologie-sexe-classe-dage-et-territoire-departement-region")


if __name__ == "__main__":
    main()
else:
    main()
