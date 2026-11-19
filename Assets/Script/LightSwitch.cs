using UnityEngine;

public class LightSwitch : MonoBehaviour
{
    [Header("Referensi Komponen Cahaya")]
    [Tooltip("Isi dengan lampu ruangan yang akan dinyalakan atau dimatikan.")]
    public Light lampuRuangan;

    public void ToggleLampu()
    {
        if (lampuRuangan == null)
        {
            Debug.LogWarning("[LIGHT SWITCH] Lampu ruangan belum di-assign di Inspector.");
            return;
        }

        lampuRuangan.enabled = !lampuRuangan.enabled;
        string status = lampuRuangan.enabled ? "MENYALA" : "PADAM";
        Debug.Log("[LIGHT SWITCH] Status lampu sekarang: " + status);
    }
}
