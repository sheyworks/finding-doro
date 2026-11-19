using UnityEngine;

public class Collectible : MonoBehaviour
{
    [Header("Collectible Settings")]
    public string collectibleName = "Koin Emas Murni";
    public int collectibleValue = 10;

    private bool hasBeenCollected;

    public void Collect()
    {
        if (hasBeenCollected) return;
        hasBeenCollected = true;

        Debug.Log("Collected: " + collectibleName + " with value: " + collectibleValue);
        if (CoinManager.Instance != null)
            CoinManager.Instance.RegisterCollectedCoin();

        Destroy(gameObject);
    }
}
