function makeform(num, traits)
{
    for (i = 0; i < num; i++)
    {
        document.getElementById("buh").innerHTML = <select></select>;
        for (i = 0; i < len(traits); i++)
        {
            document.getElementById("buh").innerHTML = <option>{traits[i]}</option>;
        }
    }
    return false;
}