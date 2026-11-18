using TMPro;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

public class PlayerAttribute : MonoBehaviour
{
    [Header("Gun Settings")]
    public GameObject gun;
    public GameObject gunUI;
    private bool isGunActive;

    [Header("Health Settings")]
    public int maxHealth = 100;
    public int currentHealth;
    public TMP_Text healthText;
    public Slider healthSlider;

    public bool IsDead => currentHealth <= 0;

    private void Awake()
    {
        if (currentHealth <= 0) currentHealth = maxHealth;
        UpdateHealthUI();
    }

    private void Update()
    {
        Keyboard keyboard = Keyboard.current;
        if (keyboard != null && keyboard.gKey.wasPressedThisFrame)
        {
            isGunActive = !isGunActive;
            SetGunActive(isGunActive);
        }
    }

    public void SetGunActive(bool isActive)
    {
        isGunActive = isActive;
        if (gun != null) gun.SetActive(isActive);
        if (gunUI != null) gunUI.SetActive(isActive);
    }

    public void TakeDamage(int damage)
    {
        if (IsDead || damage <= 0) return;

        currentHealth = Mathf.Max(0, currentHealth - damage);
        UpdateHealthUI();

        if (IsDead) Die();
    }

    private void UpdateHealthUI()
    {
        if (healthText != null) healthText.text = "Health: " + currentHealth;
        if (healthSlider != null)
        {
            healthSlider.minValue = 0;
            healthSlider.maxValue = maxHealth;
            healthSlider.value = currentHealth;
        }
    }

    private void Die()
    {
        PlayerMovement movement = GetComponent<PlayerMovement>();
        if (movement != null) movement.enabled = false;

        GameOver gameOver = FindFirstObjectByType<GameOver>();
        if (gameOver != null)
        {
            gameOver.GameOvers();
        }
        else
        {
            Debug.LogError("GameOver component was not found in the active scene.");
        }
    }
}
