using System;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEngine.InputSystem;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;

/// <summary>
/// Lightweight block-battle HUD. It builds its own Canvas at runtime, so no scene
/// prefab setup is required. Gameplay code can subscribe to the public events and
/// update health, ammo, and wave values through the public methods below.
/// </summary>
public sealed class BasicBattleHUD : MonoBehaviour
{
    public static BasicBattleHUD Instance { get; private set; }

    public event Action FireRequested;
    public event Action ReloadRequested;

    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private int magazineSize = 12;
    [SerializeField] private int reserveAmmo = 48;

    private float health;
    private int ammo;
    private int wave = 1;
    private int enemiesRemaining = 8;

    private Image healthFill;
    private Text healthValue;
    private Text ammoValue;
    private Text reserveValue;
    private Text waveValue;
    private Text enemiesValue;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void CreateForGameplayScene()
    {
        if (FindAnyObjectByType<BasicBattleHUD>() != null)
            return;

        string sceneName = SceneManager.GetActiveScene().name.ToLowerInvariant();
        bool hasPlayer = FindAnyObjectByType<PlayerMovement>() != null;
        bool isBattleScene = sceneName.Contains("battle") || sceneName.Contains("prototype") || hasPlayer;
        if (!isBattleScene)
            return;

        new GameObject("Basic Battle HUD").AddComponent<BasicBattleHUD>();
    }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        health = maxHealth;
        ammo = magazineSize;
        BuildCanvas();
    }

    private void OnDestroy()
    {
        if (Instance == this)
            Instance = null;
    }

    private void Update()
    {
        Keyboard keyboard = Keyboard.current;
        if (keyboard != null && keyboard.rKey.wasPressedThisFrame)
            Reload();

        Mouse mouse = Mouse.current;
        if (mouse != null && mouse.leftButton.wasPressedThisFrame)
            Fire();
    }

    public void SetHealth(float value)
    {
        health = Mathf.Clamp(value, 0f, maxHealth);
        RefreshHealth();
    }

    public void ApplyDamage(float amount) => SetHealth(health - Mathf.Max(0f, amount));

    public void SetAmmo(int current, int reserve)
    {
        ammo = Mathf.Clamp(current, 0, magazineSize);
        reserveAmmo = Mathf.Max(0, reserve);
        RefreshAmmo();
    }

    public void SetWave(int currentWave, int remainingEnemies)
    {
        wave = Mathf.Max(1, currentWave);
        enemiesRemaining = Mathf.Max(0, remainingEnemies);
        RefreshWave();
    }

    public void EnemyDefeated()
    {
        enemiesRemaining = Mathf.Max(0, enemiesRemaining - 1);
        RefreshWave();
    }

    public void Fire()
    {
        if (ammo <= 0)
            return;

        ammo--;
        RefreshAmmo();
        FireRequested?.Invoke();
    }

    public void Reload()
    {
        if (ammo >= magazineSize || reserveAmmo <= 0)
            return;

        int needed = magazineSize - ammo;
        int loaded = Mathf.Min(needed, reserveAmmo);
        ammo += loaded;
        reserveAmmo -= loaded;
        RefreshAmmo();
        ReloadRequested?.Invoke();
    }

    private void BuildCanvas()
    {
        Canvas canvas = new GameObject("Battle HUD Canvas", typeof(RectTransform), typeof(Canvas),
            typeof(CanvasScaler), typeof(GraphicRaycaster)).GetComponent<Canvas>();
        canvas.transform.SetParent(transform, false);
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 20;

        CanvasScaler scaler = canvas.GetComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1600f, 900f);
        scaler.matchWidthOrHeight = 0.5f;

        EnsureEventSystem();
        BuildHealthPanel(canvas.transform);
        BuildWavePanel(canvas.transform);
        BuildAmmoPanel(canvas.transform);
        BuildCrosshair(canvas.transform);
        if (Application.isMobilePlatform)
            BuildTouchButtons(canvas.transform);
    }

    private void EnsureEventSystem()
    {
        if (FindAnyObjectByType<EventSystem>() != null)
            return;

        GameObject eventSystem = new GameObject("Battle HUD EventSystem", typeof(EventSystem),
            typeof(InputSystemUIInputModule));
        eventSystem.transform.SetParent(transform, false);
    }

    private void BuildHealthPanel(Transform parent)
    {
        RectTransform panel = Panel(parent, "Health Panel", new Vector2(300, 100),
            new Vector2(0, 1), new Vector2(28, -28), new Color32(15, 34, 55, 228));
        Label(panel, "HEALTH", 15, new Vector2(16, -13), new Vector2(110, 22),
            TextAnchor.MiddleLeft, new Color32(174, 222, 236, 255));
        healthValue = Label(panel, "100 / 100", 24, new Vector2(16, -37), new Vector2(180, 31),
            TextAnchor.MiddleLeft, Color.white);

        RectTransform barBack = Panel(panel, "Health Bar Back", new Vector2(266, 13),
            new Vector2(0, 1), new Vector2(16, -78), new Color32(5, 16, 28, 255));
        healthFill = Panel(barBack, "Health Bar Fill", new Vector2(266, 13),
            new Vector2(0, 0.5f), Vector2.zero, new Color32(63, 218, 157, 255)).GetComponent<Image>();
        healthFill.rectTransform.pivot = new Vector2(0, 0.5f);
        RefreshHealth();
    }

    private void BuildWavePanel(Transform parent)
    {
        RectTransform panel = Panel(parent, "Wave Panel", new Vector2(260, 70),
            new Vector2(0.5f, 1), new Vector2(0, -24), new Color32(15, 34, 55, 220));
        waveValue = Label(panel, "WAVE 01", 25, new Vector2(10, -5), new Vector2(240, 34),
            TextAnchor.MiddleCenter, new Color32(255, 208, 73, 255));
        enemiesValue = Label(panel, "8 ENEMIES LEFT", 14, new Vector2(10, -40), new Vector2(240, 20),
            TextAnchor.MiddleCenter, new Color32(203, 228, 235, 255));
        RefreshWave();
    }

    private void BuildAmmoPanel(Transform parent)
    {
        RectTransform panel = Panel(parent, "Ammo Panel", new Vector2(260, 96),
            new Vector2(1, 1), new Vector2(-28, -28), new Color32(15, 34, 55, 228));
        Label(panel, "NUMBER PISTOL", 14, new Vector2(16, -12), new Vector2(220, 20),
            TextAnchor.MiddleLeft, new Color32(174, 222, 236, 255));
        ammoValue = Label(panel, "12", 34, new Vector2(16, -36), new Vector2(94, 42),
            TextAnchor.MiddleLeft, Color.white);
        Label(panel, "/", 25, new Vector2(105, -41), new Vector2(28, 40),
            TextAnchor.MiddleCenter, new Color32(174, 222, 236, 255));
        reserveValue = Label(panel, "48", 23, new Vector2(135, -42), new Vector2(80, 40),
            TextAnchor.MiddleLeft, new Color32(255, 208, 73, 255));
        Label(panel, "R  RELOAD", 12, new Vector2(16, -73), new Vector2(130, 18),
            TextAnchor.MiddleLeft, new Color32(174, 222, 236, 255));
        RefreshAmmo();
    }

    private void BuildCrosshair(Transform parent)
    {
        Color cross = new Color32(245, 250, 242, 245);
        Panel(parent, "Crosshair Top", new Vector2(4, 12), new Vector2(0.5f, 0.5f),
            new Vector2(0, 16), cross);
        Panel(parent, "Crosshair Bottom", new Vector2(4, 12), new Vector2(0.5f, 0.5f),
            new Vector2(0, -16), cross);
        Panel(parent, "Crosshair Left", new Vector2(12, 4), new Vector2(0.5f, 0.5f),
            new Vector2(-16, 0), cross);
        Panel(parent, "Crosshair Right", new Vector2(12, 4), new Vector2(0.5f, 0.5f),
            new Vector2(16, 0), cross);
        Panel(parent, "Crosshair Center", new Vector2(4, 4), new Vector2(0.5f, 0.5f),
            Vector2.zero, new Color32(255, 208, 73, 255));
    }

    private void BuildTouchButtons(Transform parent)
    {
        RectTransform fire = Panel(parent, "Fire Button", new Vector2(108, 108),
            new Vector2(1, 0), new Vector2(-95, 112), new Color32(229, 85, 68, 225));
        Button fireButton = fire.gameObject.AddComponent<Button>();
        fireButton.targetGraphic = fire.GetComponent<Image>();
        fire.GetComponent<Image>().raycastTarget = true;
        fireButton.onClick.AddListener(Fire);
        Label(fire, "FIRE", 19, new Vector2(4, -33), new Vector2(100, 42), TextAnchor.MiddleCenter, Color.white);

        RectTransform reload = Panel(parent, "Reload Button", new Vector2(88, 54),
            new Vector2(1, 0), new Vector2(-200, 66), new Color32(28, 139, 171, 230));
        Button reloadButton = reload.gameObject.AddComponent<Button>();
        reloadButton.targetGraphic = reload.GetComponent<Image>();
        reload.GetComponent<Image>().raycastTarget = true;
        reloadButton.onClick.AddListener(Reload);
        Label(reload, "RELOAD", 13, new Vector2(3, -7), new Vector2(82, 40), TextAnchor.MiddleCenter, Color.white);
    }

    private RectTransform Panel(Transform parent, string name, Vector2 size, Vector2 anchor,
        Vector2 position, Color color)
    {
        GameObject go = new GameObject(name, typeof(RectTransform), typeof(CanvasRenderer), typeof(Image));
        go.transform.SetParent(parent, false);
        RectTransform rect = go.GetComponent<RectTransform>();
        rect.anchorMin = anchor;
        rect.anchorMax = anchor;
        rect.pivot = new Vector2(anchor.x == 1 ? 1 : anchor.x, anchor.y == 0 ? 0 : anchor.y);
        rect.sizeDelta = size;
        rect.anchoredPosition = position;
        Image image = go.GetComponent<Image>();
        image.color = color;
        image.raycastTarget = false;
        return rect;
    }

    private Text Label(Transform parent, string value, int size, Vector2 position,
        Vector2 bounds, TextAnchor alignment, Color color)
    {
        GameObject go = new GameObject(value + " Label", typeof(RectTransform), typeof(CanvasRenderer), typeof(Text));
        go.transform.SetParent(parent, false);
        RectTransform rect = go.GetComponent<RectTransform>();
        rect.anchorMin = rect.anchorMax = new Vector2(0, 1);
        rect.pivot = new Vector2(0, 1);
        rect.sizeDelta = bounds;
        rect.anchoredPosition = position;
        Text text = go.GetComponent<Text>();
        text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        text.text = value;
        text.fontSize = size;
        text.fontStyle = FontStyle.Bold;
        text.alignment = alignment;
        text.color = color;
        text.raycastTarget = false;
        return text;
    }

    private void RefreshHealth()
    {
        if (healthValue != null)
            healthValue.text = $"{Mathf.CeilToInt(health)} / {Mathf.CeilToInt(maxHealth)}";
        if (healthFill != null)
        {
            float ratio = maxHealth <= 0f ? 0f : health / maxHealth;
            healthFill.rectTransform.sizeDelta = new Vector2(266f * ratio, 13f);
            healthFill.color = ratio > 0.55f ? new Color32(63, 218, 157, 255)
                : ratio > 0.25f ? new Color32(255, 190, 64, 255)
                : new Color32(244, 83, 76, 255);
        }
    }

    private void RefreshAmmo()
    {
        if (ammoValue != null) ammoValue.text = ammo.ToString("00");
        if (reserveValue != null) reserveValue.text = reserveAmmo.ToString("00");
    }

    private void RefreshWave()
    {
        if (waveValue != null) waveValue.text = $"WAVE {wave:00}";
        if (enemiesValue != null) enemiesValue.text = $"{enemiesRemaining} ENEMIES LEFT";
    }
}
