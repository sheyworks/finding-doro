using UnityEngine;
using UnityEngine.UI;

public class Enemy : MonoBehaviour
{
    [Header("Health")]
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private Slider healthSlider;
    [SerializeField] private int bulletDamage = 20;

    [Header("Chase and Attack")]
    [SerializeField] private float detectionRadius = 10f;
    [SerializeField] private float attackRange = 1.5f;
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private int attackDamage = 10;
    [SerializeField] private float attackCooldown = 1f;

    private int currentHealth;
    private PlayerMovement targetPlayer;
    private PlayerAttribute playerHealth;
    private float nextAttackTime;
    private bool isDead;

    private void Awake()
    {
        currentHealth = maxHealth;
        if (healthSlider != null)
        {
            healthSlider.minValue = 0;
            healthSlider.maxValue = maxHealth;
            healthSlider.value = currentHealth;
        }
    }

    private void Update()
    {
        FindPlayer();
        if (targetPlayer == null || playerHealth == null || playerHealth.IsDead) return;

        Vector3 toPlayer = targetPlayer.transform.position - transform.position;
        toPlayer.y = 0f;
        float distance = toPlayer.magnitude;
        if (distance > detectionRadius) return;

        if (toPlayer.sqrMagnitude > 0.001f)
        {
            transform.rotation = Quaternion.LookRotation(toPlayer.normalized, Vector3.up);
        }

        if (distance <= attackRange)
        {
            if (Time.time >= nextAttackTime)
            {
                playerHealth.TakeDamage(attackDamage);
                nextAttackTime = Time.time + attackCooldown;
            }

            return;
        }

        Vector3 destination = targetPlayer.transform.position;
        destination.y = transform.position.y;
        transform.position = Vector3.MoveTowards(
            transform.position,
            destination,
            moveSpeed * Time.deltaTime);
    }

    private void FindPlayer()
    {
        if (targetPlayer != null && playerHealth != null) return;

        targetPlayer = FindFirstObjectByType<PlayerMovement>();
        if (targetPlayer == null) return;

        playerHealth = targetPlayer.GetComponent<PlayerAttribute>();
        if (playerHealth == null)
        {
            playerHealth = targetPlayer.GetComponentInParent<PlayerAttribute>();
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Bullet"))
        {
            TakeDamage(bulletDamage);
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Bullet"))
        {
            TakeDamage(bulletDamage);
        }
    }

    public void TakeDamage(int damage)
    {
        if (isDead || damage <= 0) return;

        currentHealth = Mathf.Max(0, currentHealth - damage);
        if (healthSlider != null) healthSlider.value = currentHealth;

        if (currentHealth == 0)
        {
            isDead = true;
            Destroy(gameObject);
        }
    }
}

