using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class CoinManager : MonoBehaviour
{
    public static CoinManager Instance { get; private set; }

    [Header("Coin Spawn")]
    [Tooltip("GameObject area. Tambahkan Collider atau Renderer untuk menentukan batas area.")]
    public GameObject spawnAreaObject;
    [Tooltip("Coin contoh/prefab yang akan diduplikasi.")]
    public GameObject coinPrefab;
    [Min(1)] public int coinsToSpawn = 20;
    [SerializeField] private float coinHeightAboveGround = 0.15f;
    [SerializeField] private bool spawnOnStart = true;

    [Header("Coin Count")]
    [SerializeField] private int collectedCoins;
    [SerializeField] private TMP_Text coinCountText;

    private bool hasSpawned;

    public int CollectedCoins => collectedCoins;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Debug.LogWarning("Ada lebih dari satu CoinManager di scene.");
            return;
        }

        Instance = this;
    }

    private void Start()
    {
        CreateCounterIfNeeded();
        RefreshCounter();
        if (spawnOnStart) SpawnCoinsOnce();
    }

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    public void RegisterCollectedCoin()
    {
        collectedCoins++;
        RefreshCounter();
        Debug.Log("[COIN COUNT] " + collectedCoins + " / " + coinsToSpawn);
    }

    public void SpawnCoinsOnce()
    {
        if (hasSpawned) return;
        hasSpawned = true;

        if (spawnAreaObject == null)
        {
            Debug.LogWarning("[COIN SPAWN] Isi Spawn Area Object di Inspector dulu.");
            return;
        }

        if (coinPrefab == null)
        {
            Debug.LogWarning("[COIN SPAWN] Isi Coin Prefab di Inspector dulu.");
            return;
        }

        EnsureCoinComponents(coinPrefab);
        coinPrefab.transform.position = GetRandomSpawnPosition();
        coinPrefab.SetActive(true);

        for (int i = 1; i < coinsToSpawn; i++)
        {
            GameObject coin = Instantiate(coinPrefab, GetRandomSpawnPosition(), coinPrefab.transform.rotation);
            EnsureCoinComponents(coin);
            coin.SetActive(true);
        }

        Debug.Log("[COIN SPAWN] Berhasil menaruh " + coinsToSpawn + " coin di area.");
    }

    private Vector3 GetRandomSpawnPosition()
    {
        Collider areaCollider = spawnAreaObject.GetComponent<Collider>();
        Bounds areaBounds = GetAreaBounds(areaCollider);
        Vector3 pointOnTop;

        BoxCollider box = areaCollider as BoxCollider;
        if (box != null)
        {
            Vector3 localPoint = box.center + new Vector3(
                Random.Range(-box.size.x * 0.5f, box.size.x * 0.5f),
                box.size.y * 0.5f,
                Random.Range(-box.size.z * 0.5f, box.size.z * 0.5f));
            pointOnTop = box.transform.TransformPoint(localPoint);
        }
        else
        {
            pointOnTop = new Vector3(
                Random.Range(areaBounds.min.x, areaBounds.max.x),
                areaBounds.max.y + 5f,
                Random.Range(areaBounds.min.z, areaBounds.max.z));
        }

        RaycastHit[] hits = Physics.RaycastAll(
            pointOnTop,
            Vector3.down,
            100f,
            Physics.DefaultRaycastLayers,
            QueryTriggerInteraction.Ignore);

        float nearestDistance = float.MaxValue;
        Vector3 spawnPosition = new Vector3(pointOnTop.x, areaBounds.max.y + coinHeightAboveGround, pointOnTop.z);
        Transform areaRoot = spawnAreaObject.transform;
        Transform coinRoot = coinPrefab != null ? coinPrefab.transform : null;

        foreach (RaycastHit hit in hits)
        {
            if (hit.collider == null) continue;
            Transform hitTransform = hit.collider.transform;
            if (hitTransform == areaRoot || hitTransform.IsChildOf(areaRoot)) continue;
            if (coinRoot != null && (hitTransform == coinRoot || hitTransform.IsChildOf(coinRoot))) continue;
            if (hitTransform.root.CompareTag("Player")) continue;

            if (hit.distance < nearestDistance)
            {
                nearestDistance = hit.distance;
                spawnPosition = hit.point + Vector3.up * coinHeightAboveGround;
            }
        }

        return spawnPosition;
    }

    private Bounds GetAreaBounds(Collider areaCollider)
    {
        if (areaCollider != null) return areaCollider.bounds;

        Renderer areaRenderer = spawnAreaObject.GetComponent<Renderer>();
        if (areaRenderer != null) return areaRenderer.bounds;

        Vector3 size = spawnAreaObject.transform.lossyScale;
        size.x = Mathf.Max(1f, Mathf.Abs(size.x));
        size.y = Mathf.Max(1f, Mathf.Abs(size.y));
        size.z = Mathf.Max(1f, Mathf.Abs(size.z));
        return new Bounds(spawnAreaObject.transform.position, size);
    }

    private void EnsureCoinComponents(GameObject coin)
    {
        if (coin.GetComponent<Collectible>() == null)
            coin.AddComponent<Collectible>();
        if (coin.GetComponent<CoinSpin>() == null)
            coin.AddComponent<CoinSpin>();

        if (!coin.CompareTag("Collectible"))
            coin.tag = "Collectible";
    }

    private void CreateCounterIfNeeded()
    {
        if (coinCountText != null) return;

        Canvas canvas = FindFirstObjectByType<Canvas>();
        if (canvas == null)
        {
            Debug.LogWarning("[COIN COUNT] Canvas tidak ditemukan; count tetap tersedia di Console.");
            return;
        }

        GameObject counter = new GameObject("Coin Count", typeof(RectTransform), typeof(CanvasRenderer), typeof(Text));
        counter.transform.SetParent(canvas.transform, false);
        RectTransform rect = counter.GetComponent<RectTransform>();
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.zero;
        rect.pivot = Vector2.zero;
        rect.anchoredPosition = new Vector2(24f, 24f);
        rect.sizeDelta = new Vector2(220f, 42f);

        coinCountText = counter.GetComponent<TMP_Text>();
        // coinCountText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        coinCountText.fontSize = 24;
        // coinCountText.fontStyle = FontStyle.Bold;
        // coinCountText.alignment = TextAnchor.MiddleLeft;
        coinCountText.color = Color.white;
        coinCountText.raycastTarget = false;
    }

    private void RefreshCounter()
    {
        if (coinCountText != null)
            coinCountText.text = "COINS " + collectedCoins + " / " + coinsToSpawn;
    }
}
